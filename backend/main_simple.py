"""
Simple FastAPI Backend for Visual Search Engine (without ML models)
For testing and demonstration purposes
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from pathlib import Path

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

# Response models
class DetectionResult(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]

class SearchResult(BaseModel):
    id: str
    similarity: float
    metadata: dict

class UploadResponse(BaseModel):
    success: bool
    detections: List[DetectionResult]
    image_id: str

class SimilarityResponse(BaseModel):
    success: bool
    results: List[SearchResult]

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Visual Search Engine API (Demo Mode)",
        "version": "1.0.0",
        "models": {
            "detector": False,
            "embedder": False,
            "vector_store": False
        },
        "note": "This is a demo version without ML models loaded"
    }

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    # Return a simple response instead of a file
    return JSONResponse(content={"message": "No favicon available"}, status_code=200)

@app.post("/detect", response_model=UploadResponse)
async def detect_objects(file: UploadFile = File(...)):
    """Demo object detection endpoint"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Demo response
    import hashlib
    image_bytes = await file.read()
    image_id = hashlib.md5(image_bytes).hexdigest()
    
    return UploadResponse(
        success=True,
        detections=[
            DetectionResult(
                class_name="person",
                confidence=0.95,
                bbox=[100, 150, 300, 450]
            ),
            DetectionResult(
                class_name="car",
                confidence=0.87,
                bbox=[400, 200, 600, 350]
            )
        ],
        image_id=image_id
    )

@app.post("/search", response_model=SimilarityResponse)
async def search_similar(
    file: UploadFile = File(...),
    top_k: int = Form(default=5)
):
    """Demo similarity search endpoint"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Demo response
    return SimilarityResponse(
        success=True,
        results=[
            SearchResult(
                id="demo_img_001",
                similarity=0.92,
                metadata={"category": "furniture", "object_name": "red_chair"}
            ),
            SearchResult(
                id="demo_img_002",
                similarity=0.87,
                metadata={"category": "furniture", "object_name": "blue_chair"}
            )
        ]
    )

@app.post("/index")
async def index_image(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(default="{}")
):
    """Demo image indexing endpoint"""
    import hashlib
    import json
    
    image_bytes = await file.read()
    image_id = hashlib.md5(image_bytes).hexdigest()
    
    return {
        "success": True,
        "image_id": image_id,
        "message": "Image indexed successfully (demo mode)"
    }

@app.get("/stats")
async def get_stats():
    """Demo database statistics"""
    return {
        "success": True,
        "stats": {
            "total_items": 0,
            "collection_name": "demo_collection",
            "note": "Demo mode - no actual data stored"
        }
    }

@app.delete("/clear")
async def clear_database():
    """Demo clear database endpoint"""
    return {
        "success": True,
        "message": "Database cleared (demo mode)"
    }

if __name__ == "__main__":
    print("Starting Visual Search Engine (Demo Mode)...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Note: This is a demo version without ML models")
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
