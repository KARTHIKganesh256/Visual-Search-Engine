"""
FastAPI Backend for Visual Search Engine
Handles image uploads, object detection, and similarity search
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from pathlib import Path
import sys
import mimetypes

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.ml_models.detector import ObjectDetector
from backend.ml_models.embedder import ImageEmbedder
from backend.database.vector_store import VectorStore
from backend.ml_models.captioner import ImageCaptioner
from backend.utils.image_processor import ImageProcessor
from backend.utils.logger import setup_logger

# Initialize logger
logger = setup_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Visual Search Engine API",
    description="Free & Open Source Visual Search API",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances (lazy loading)
detector = None
embedder = None
captioner = None
vector_store = None
image_processor = ImageProcessor()
models_initialized = False


def _resolve_content_type(file: UploadFile) -> Optional[str]:
    """
    Ensure we treat uploads from browsers that omit content_type properly.
    """
    content_type = getattr(file, "content_type", None)
    if not content_type:
        filename = getattr(file, "filename", None)
        if filename:
            guessed, _ = mimetypes.guess_type(filename)
            content_type = guessed
    return content_type


def _ensure_models(*names: str):
    """
    Make sure referenced models are available. If any are missing, attempt
    to initialize them lazily. Raises HTTPException if still unavailable.
    """
    global detector, embedder, captioner, vector_store, models_initialized

    missing = [name for name in names if globals().get(name) is None]
    if missing and not models_initialized:
        try:
            startup_event()
        except Exception as init_err:
            logger.error(f"Model init failed: {init_err}")
            raise HTTPException(
                status_code=503,
                detail="Required models are not ready. Please retry in a moment."
            )

    resolved = []
    for name in names:
        component = globals().get(name)
        if component is None:
            raise HTTPException(
                status_code=503,
                detail=f"{name.replace('_', ' ').title()} unavailable"
            )
        resolved.append(component)

    return resolved if len(resolved) > 1 else resolved[0]

# Response models
class DetectionResult(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]

class SearchResult(BaseModel):
    id: str
    name: str
    similarity: float

class UploadResponse(BaseModel):
    success: bool
    detections: List[DetectionResult]
    image_id: str

class SimilarityResponse(BaseModel):
    success: bool
    results: List[SearchResult]


class CaptionResponse(BaseModel):
    success: bool
    caption: str


def startup_event():
    """Initialize models on startup"""
    global detector, embedder, captioner, vector_store, models_initialized

    if models_initialized:
        return detector, embedder, captioner, vector_store

    logger.info("Initializing ML models...")

    try:
        # Initialize object detector (YOLOv8)
        detector = ObjectDetector(model_size='n')  # 'n' for nano (fastest)
        logger.info("✓ Object detector loaded")

        # Initialize embedder (CLIP)
        embedder = ImageEmbedder(model_name='openai/clip-vit-base-patch32')
        logger.info("✓ Image embedder loaded")

        # Initialize captioner (BLIP)
        try:
            captioner = ImageCaptioner()
            logger.info("✓ Captioner (BLIP) loaded")
        except Exception as ce:
            captioner = None
            logger.warning(f"Captioner not available: {ce}")

        # Initialize vector store (ChromaDB)
        vector_store = VectorStore(persist_directory="./data/chroma")
        logger.info("✓ Vector store initialized")

        logger.info("All models loaded successfully!")
        models_initialized = True
        return detector, embedder, captioner, vector_store

    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise


@app.on_event("startup")
async def startup_event_async():
    startup_event()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Visual Search Engine API",
        "version": "1.0.0",
        "models": {
            "detector": detector is not None,
            "embedder": embedder is not None,
            "vector_store": vector_store is not None
        }
    }

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    return JSONResponse(content={"message": "No favicon available"}, status_code=200)


@app.post("/detect", response_model=UploadResponse)
async def detect_objects(file: UploadFile = File(...)):
    """
    Detect objects in uploaded image
    
    Args:
        file: Image file (JPEG, PNG)
        
    Returns:
        Detection results with bounding boxes and confidence scores
    """
    try:
        # Read and process image
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image upload")

        # Validate file type (some browsers may omit content_type)
        content_type = _resolve_content_type(file)
        if content_type:
            if not content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
        else:
            if not image_processor.validate_image(image_bytes):
                raise HTTPException(status_code=400, detail="File must be an image")

        detector_model = _ensure_models("detector")
        processed_image = image_processor.preprocess(image_bytes)
        
        # Run object detection
        detections = detector_model.detect(processed_image)
        
        # Format results
        detection_results = []
        for det in detections:
            detection_results.append(DetectionResult(
                class_name=det['class'],
                confidence=float(det['confidence']),
                bbox=det['bbox']
            ))
        
        # Generate unique image ID
        import hashlib
        image_id = hashlib.md5(image_bytes).hexdigest()
        
        logger.info(f"Detected {len(detection_results)} objects in image {image_id}")
        
        return UploadResponse(
            success=True,
            detections=detection_results,
            image_id=image_id
        )
        
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/caption", response_model=CaptionResponse)
async def generate_caption(file: UploadFile = File(...)):
    """Generate a natural-language caption for an image using BLIP."""
    try:
        if captioner is None:
            raise HTTPException(status_code=503, detail="Captioner not available")

        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image upload")

        content_type = _resolve_content_type(file)
        if content_type:
            if not content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
        else:
            if not image_processor.validate_image(image_bytes):
                raise HTTPException(status_code=400, detail="File must be an image")

        processed_image = image_processor.preprocess(image_bytes)
        captioner_model = _ensure_models("captioner")
        text = captioner_model.caption(processed_image)
        return CaptionResponse(success=True, caption=text)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Caption error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SimilarityResponse)
async def search_similar(
    file: UploadFile = File(...),
    top_k: int = Form(default=5)
):
    """
    Search for similar images using visual embeddings
    
    Args:
        file: Query image file
        top_k: Number of similar results to return
        
    Returns:
        List of similar images with similarity scores
    """
    try:
        # Validate input
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image upload")

        content_type = _resolve_content_type(file)
        if content_type:
            if not content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
        else:
            if not image_processor.validate_image(image_bytes):
                raise HTTPException(status_code=400, detail="File must be an image")

        if top_k < 1 or top_k > 50:
            raise HTTPException(status_code=400, detail="top_k must be between 1 and 50")

        processed_image = image_processor.preprocess(image_bytes)
        
        # Generate embedding
        embedder_model, vector_db = _ensure_models("embedder", "vector_store")
        embedding = embedder_model.embed(processed_image)
        
        # Search vector store
        results = vector_db.search(embedding, top_k=top_k)
        
        # Format results
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                id=result['id'],
                name=result.get('metadata', {}).get('name', 'Unknown'),
                similarity=float(result['similarity'])
            ))
        
        logger.info(f"Found {len(search_results)} similar images")
        
        return SimilarityResponse(
            success=True,
            results=search_results
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
async def index_image(
    file: UploadFile = File(...),
    name: Optional[str] = Form(default=None)
):
    """
    Add image to vector database for future searches
    
    Args:
        file: Image file to index
        name: Name/label for the image
        
    Returns:
        Success status and image details
    """
    try:
        from datetime import datetime
        import hashlib
        
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image upload")

        content_type = _resolve_content_type(file)
        if content_type:
            if not content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
        else:
            if not image_processor.validate_image(image_bytes):
                raise HTTPException(status_code=400, detail="File must be an image")

        processed_image = image_processor.preprocess(image_bytes)
        
        # Auto-generate name if not provided using captioner, fallback to detector
        auto_name = None
        try:
            captioner_model = _ensure_models("captioner")
            auto_name = captioner_model.caption(processed_image)
        except Exception:
            auto_name = None
        if not auto_name:
            try:
                detector_model = _ensure_models("detector")
                detections = detector_model.detect(processed_image)
                if detections:
                    best = max(detections, key=lambda d: float(d.get("confidence", 0)))
                    auto_name = best.get("class", None)
            except Exception:
                auto_name = None
        
        if not name:
            name = auto_name
        
        # Fallback if still empty
        if not name:
            from hashlib import md5
            name = f"image-{md5(image_bytes).hexdigest()[:8]}"
        
        # Generate embedding
        embedder_model, vector_db = _ensure_models("embedder", "vector_store")
        embedding = embedder_model.embed(processed_image)
        
        # Generate ID
        image_id = hashlib.md5(image_bytes).hexdigest()
        
        # Create metadata with name
        timestamp = datetime.now().isoformat()
        metadata_dict = {
            "name": name,
            "timestamp": timestamp
        }
        
        # Add to vector store
        vector_db.add(
            embeddings=[embedding],
            ids=[image_id],
            metadatas=[metadata_dict]
        )
        
        logger.info(f"Indexed image {image_id} with name: {name}")
        
        return {
            "id": image_id,
            "name": name,
            "status": "indexed",
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"Indexing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        vector_db = _ensure_models("vector_store")
        # Get all items from database
        all_data = vector_db.collection.get(include=['metadatas'])
        
        # Build indexed images list
        indexed_images = []
        for i, img_id in enumerate(all_data['ids']):
            metadata = all_data['metadatas'][i] if all_data['metadatas'] else {}
            indexed_images.append({
                'id': img_id,
                'name': metadata.get('name', 'Unknown'),
                'timestamp': metadata.get('timestamp', '')
            })
        
        return {
            "total_images": len(all_data['ids']),
            "indexed_images": indexed_images
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/clear")
async def clear_database():
    """Clear all indexed images (admin only - add auth in production)"""
    try:
        vector_db = _ensure_models("vector_store")
        vector_db.clear()
        return {
            "success": True,
            "message": "Database cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run with: python main.py
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

