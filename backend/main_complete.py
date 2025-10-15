"""
Complete Visual Search Engine Backend
FastAPI application with image indexing and similarity search
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
import uvicorn
import base64
import io
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from PIL import Image
import uuid
from datetime import datetime
import json

# Initialize FastAPI app
app = FastAPI(
    title="Visual Search Engine API",
    description="Complete Visual Search Engine with ResNet50 embeddings",
    version="2.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for storing embeddings and metadata
embeddings_store: List[Dict] = []
model = None
transform = None

# Pydantic models for request/response
class IndexRequest(BaseModel):
    name: str = Field(..., description="Name/label for the image")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")

class SearchRequest(BaseModel):
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")

class IndexResponse(BaseModel):
    id: str
    name: str
    status: str = "indexed"
    timestamp: str

class SearchResult(BaseModel):
    name: str
    similarity: float
    id: str

class SearchResponse(BaseModel):
    results: List[SearchResult]

class StatsResponse(BaseModel):
    total_images: int
    indexed_images: List[Dict]

def initialize_model():
    """Initialize ResNet50 model for feature extraction"""
    global model, transform
    
    print("Loading ResNet50 model...")
    
    # Load pre-trained ResNet50
    weights = ResNet50_Weights.IMAGENET1K_V2
    model = resnet50(weights=weights)
    model.eval()  # Set to evaluation mode
    
    # Get the transform for preprocessing
    transform = weights.transforms()
    
    print("✓ ResNet50 model loaded successfully")

def extract_features(image: Image.Image) -> np.ndarray:
    """Extract features from image using ResNet50"""
    global model, transform
    
    if model is None or transform is None:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    # Preprocess image
    input_tensor = transform(image).unsqueeze(0)
    
    # Extract features (remove classification layer)
    with torch.no_grad():
        features = model(input_tensor)
        # Use features before final classification layer
        features = features.squeeze().numpy()
    
    # Normalize features for cosine similarity
    features = features / np.linalg.norm(features)
    
    return features

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors"""
    return np.dot(a, b)

@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    initialize_model()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Visual Search Engine API",
        "version": "2.0.0",
        "model": "ResNet50",
        "total_images": len(embeddings_store)
    }

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    return JSONResponse(content={"message": "No favicon available"}, status_code=200)

@app.post("/index", response_model=IndexResponse)
async def index_image(
    file: Optional[UploadFile] = File(None),
    name: Optional[str] = Form(None),
    image_base64: Optional[str] = Form(None)
):
    """
    Index an image with metadata
    
    Accepts either:
    - File upload with name field
    - Base64 encoded image with name field
    """
    try:
        # Validate inputs
        if not name:
            raise HTTPException(status_code=422, detail="Name field is required")
        
        # Get image data
        if file and file.filename:
            # Handle file upload
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=422, detail="File must be an image")
            
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
            
        elif image_base64:
            # Handle base64 image
            try:
                # Remove data URL prefix if present
                if image_base64.startswith('data:image'):
                    image_base64 = image_base64.split(',')[1]
                
                image_data = base64.b64decode(image_base64)
                image = Image.open(io.BytesIO(image_data))
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"Invalid base64 image: {str(e)}")
        else:
            raise HTTPException(status_code=422, detail="Either file or image_base64 is required")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract features
        features = extract_features(image)
        
        # Generate unique ID
        image_id = str(uuid.uuid4())
        
        # Store in memory
        embeddings_store.append({
            "id": image_id,
            "name": name,
            "features": features.tolist(),
            "timestamp": datetime.now().isoformat(),
            "image_size": image.size
        })
        
        return IndexResponse(
            id=image_id,
            name=name,
            status="indexed",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing image: {str(e)}")

@app.post("/search", response_model=SearchResponse)
async def search_similar(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    top_k: int = Form(default=3)
):
    """
    Search for similar images
    
    Accepts either:
    - File upload
    - Base64 encoded image
    """
    try:
        if not embeddings_store:
            return SearchResponse(results=[])
        
        # Get image data
        if file and file.filename:
            # Handle file upload
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=422, detail="File must be an image")
            
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
            
        elif image_base64:
            # Handle base64 image
            try:
                # Remove data URL prefix if present
                if image_base64.startswith('data:image'):
                    image_base64 = image_base64.split(',')[1]
                
                image_data = base64.b64decode(image_base64)
                image = Image.open(io.BytesIO(image_data))
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"Invalid base64 image: {str(e)}")
        else:
            raise HTTPException(status_code=422, detail="Either file or image_base64 is required")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract features from query image
        query_features = extract_features(image)
        
        # Compute similarities
        similarities = []
        for item in embeddings_store:
            stored_features = np.array(item["features"])
            similarity = cosine_similarity(query_features, stored_features)
            similarities.append({
                "id": item["id"],
                "name": item["name"],
                "similarity": float(similarity)
            })
        
        # Sort by similarity (descending) and take top_k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        top_results = similarities[:top_k]
        
        return SearchResponse(results=[
            SearchResult(
                name=result["name"],
                similarity=result["similarity"],
                id=result["id"]
            ) for result in top_results
        ])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching images: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get statistics about indexed images"""
    return StatsResponse(
        total_images=len(embeddings_store),
        indexed_images=[
            {
                "id": item["id"],
                "name": item["name"],
                "timestamp": item["timestamp"],
                "image_size": item["image_size"]
            } for item in embeddings_store
        ]
    )

@app.delete("/clear")
async def clear_all():
    """Clear all indexed images"""
    global embeddings_store
    count = len(embeddings_store)
    embeddings_store = []
    
    return {
        "message": f"Cleared {count} indexed images",
        "status": "success"
    }

if __name__ == "__main__":
    print("Starting Visual Search Engine Backend...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/")
    
    uvicorn.run(
        "main_complete:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

