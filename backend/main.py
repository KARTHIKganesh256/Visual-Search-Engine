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

from backend.ml_models.detector import ObjectDetector
from backend.ml_models.embedder import ImageEmbedder
from backend.database.vector_store import VectorStore
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
vector_store = None
image_processor = ImageProcessor()

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


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global detector, embedder, vector_store
    
    logger.info("Initializing ML models...")
    
    try:
        # Initialize object detector (YOLOv8)
        detector = ObjectDetector(model_size='n')  # 'n' for nano (fastest)
        logger.info("✓ Object detector loaded")
        
        # Initialize embedder (CLIP)
        embedder = ImageEmbedder(model_name='openai/clip-vit-base-patch32')
        logger.info("✓ Image embedder loaded")
        
        # Initialize vector store (ChromaDB)
        vector_store = VectorStore(persist_directory="./data/chroma")
        logger.info("✓ Vector store initialized")
        
        logger.info("All models loaded successfully!")
        
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise


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
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_bytes = await file.read()
        processed_image = image_processor.preprocess(image_bytes)
        
        # Run object detection
        detections = detector.detect(processed_image)
        
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
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        if top_k < 1 or top_k > 50:
            raise HTTPException(status_code=400, detail="top_k must be between 1 and 50")
        
        # Process image
        image_bytes = await file.read()
        processed_image = image_processor.preprocess(image_bytes)
        
        # Generate embedding
        embedding = embedder.embed(processed_image)
        
        # Search vector store
        results = vector_store.search(embedding, top_k=top_k)
        
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
    name: str = Form(...)
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
        
        # Process image
        image_bytes = await file.read()
        processed_image = image_processor.preprocess(image_bytes)
        
        # Generate embedding
        embedding = embedder.embed(processed_image)
        
        # Generate ID
        image_id = hashlib.md5(image_bytes).hexdigest()
        
        # Create metadata with name
        timestamp = datetime.now().isoformat()
        metadata_dict = {
            "name": name,
            "timestamp": timestamp
        }
        
        # Add to vector store
        vector_store.add(
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
        # Get all items from database
        all_data = vector_store.collection.get(include=['metadatas'])
        
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
        vector_store.clear()
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

