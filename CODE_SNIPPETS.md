# Code Snippets & Examples

Complete code examples for all major components of the Visual Search Engine.

## 📋 Table of Contents

1. [Image Upload & Preprocessing](#image-upload--preprocessing)
2. [Object Detection with YOLOv8](#object-detection-with-yolov8)
3. [Visual Embeddings with CLIP](#visual-embeddings-with-clip)
4. [Vector Database Operations](#vector-database-operations)
5. [REST API Examples](#rest-api-examples)
6. [Frontend Examples](#frontend-examples)
7. [Model Optimization](#model-optimization)
8. [Data Collection](#data-collection)

---

## Image Upload & Preprocessing

### Basic Image Loading

```python
from PIL import Image
import requests
from io import BytesIO

# Load from URL
def load_image_from_url(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image

# Load from file
def load_image_from_file(file_path):
    image = Image.open(file_path)
    return image

# Example
image = load_image_from_url('https://ultralytics.com/images/bus.jpg')
print(f"Image size: {image.size}")
print(f"Image mode: {image.mode}")
```

### Image Preprocessing

```python
from PIL import Image
import numpy as np

class ImagePreprocessor:
    def __init__(self, target_size=(640, 640)):
        self.target_size = target_size
    
    def resize_keep_aspect(self, image, max_size=640):
        """Resize keeping aspect ratio"""
        width, height = image.size
        
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def normalize(self, image):
        """Convert to numpy and normalize"""
        img_array = np.array(image).astype(np.float32) / 255.0
        return img_array
    
    def preprocess(self, image):
        """Full preprocessing pipeline"""
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize
        image = self.resize_keep_aspect(image)
        
        return image

# Usage
preprocessor = ImagePreprocessor()
processed_image = preprocessor.preprocess(image)
```

### Batch Image Processing

```python
from pathlib import Path
from PIL import Image

def process_image_directory(directory, output_dir, max_size=640):
    """Process all images in a directory"""
    input_path = Path(directory)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for image_file in input_path.glob('*.jpg'):
        try:
            # Load image
            image = Image.open(image_file)
            
            # Preprocess
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize
            width, height = image.size
            if width > max_size or height > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save
            output_file = output_path / image_file.name
            image.save(output_file, 'JPEG', quality=85, optimize=True)
            
            print(f"✓ Processed: {image_file.name}")
            
        except Exception as e:
            print(f"✗ Error processing {image_file.name}: {str(e)}")

# Usage
process_image_directory('raw_images/', 'processed_images/')
```

---

## Object Detection with YOLOv8

### Basic Object Detection

```python
from ultralytics import YOLO
from PIL import Image

# Load model
model = YOLO('yolov8n.pt')  # nano model

# Detect objects
image = Image.open('test.jpg')
results = model(image)

# Process results
for result in results:
    boxes = result.boxes
    
    for box in boxes:
        # Get coordinates
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        
        # Get class and confidence
        cls_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = model.names[cls_id]
        
        print(f"Found: {class_name} ({confidence:.2f})")
        print(f"  Location: ({x1:.0f}, {y1:.0f}) to ({x2:.0f}, {y2:.0f})")
```

### Advanced Detection with Filtering

```python
class ObjectDetector:
    def __init__(self, model_size='n', confidence_threshold=0.25):
        self.model = YOLO(f'yolov8{model_size}.pt')
        self.confidence_threshold = confidence_threshold
    
    def detect_with_filters(self, image, allowed_classes=None, min_area=100):
        """
        Detect objects with filtering
        
        Args:
            image: PIL Image
            allowed_classes: List of allowed class names (None = all)
            min_area: Minimum bounding box area
        """
        results = self.model(image, conf=self.confidence_threshold, verbose=False)
        
        detections = []
        
        for result in results:
            for box in result.boxes:
                # Get info
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = self.model.names[cls_id]
                
                # Calculate area
                area = (x2 - x1) * (y2 - y1)
                
                # Apply filters
                if allowed_classes and class_name not in allowed_classes:
                    continue
                
                if area < min_area:
                    continue
                
                detections.append({
                    'class': class_name,
                    'confidence': confidence,
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'area': float(area)
                })
        
        return detections

# Usage
detector = ObjectDetector()

# Only detect furniture
detections = detector.detect_with_filters(
    image,
    allowed_classes=['chair', 'couch', 'bed', 'table'],
    min_area=500
)

print(f"Found {len(detections)} furniture items")
```

### Batch Detection

```python
def detect_batch(model, images, batch_size=8):
    """
    Process multiple images efficiently
    
    Args:
        model: YOLO model
        images: List of PIL Images
        batch_size: Batch size for processing
    """
    all_detections = []
    
    for i in range(0, len(images), batch_size):
        batch = images[i:i+batch_size]
        
        # Process batch
        results = model(batch, verbose=False)
        
        # Extract detections
        for result in results:
            detections = []
            
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                detections.append({
                    'class': model.names[cls_id],
                    'confidence': confidence,
                    'bbox': [float(x1), float(y1), float(x2), float(y2)]
                })
            
            all_detections.append(detections)
    
    return all_detections

# Usage
model = YOLO('yolov8n.pt')
images = [Image.open(f'image_{i}.jpg') for i in range(10)]
results = detect_batch(model, images, batch_size=4)
```

---

## Visual Embeddings with CLIP

### Generate Image Embeddings

```python
import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

class CLIPEmbedder:
    def __init__(self, model_name='openai/clip-vit-base-patch32'):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()
    
    def embed_image(self, image):
        """Generate embedding for single image"""
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            features = self.model.get_image_features(**inputs)
            features = F.normalize(features, p=2, dim=-1)
        
        return features.cpu().numpy()[0]
    
    def embed_batch(self, images):
        """Generate embeddings for multiple images"""
        inputs = self.processor(images=images, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            features = self.model.get_image_features(**inputs)
            features = F.normalize(features, p=2, dim=-1)
        
        return features.cpu().numpy()

# Usage
embedder = CLIPEmbedder()

image = Image.open('product.jpg')
embedding = embedder.embed_image(image)

print(f"Embedding shape: {embedding.shape}")
print(f"Embedding norm: {np.linalg.norm(embedding):.3f}")  # Should be ~1.0
```

### Text-to-Image Search

```python
class MultiModalSearch:
    def __init__(self, model_name='openai/clip-vit-base-patch32'):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()
    
    def embed_text(self, text):
        """Generate embedding for text"""
        inputs = self.processor(text=text, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            features = self.model.get_text_features(**inputs)
            features = F.normalize(features, p=2, dim=-1)
        
        return features.cpu().numpy()[0]
    
    def search_by_text(self, text_query, image_embeddings, top_k=5):
        """
        Search images using text query
        
        Args:
            text_query: Text description
            image_embeddings: numpy array of image embeddings
            top_k: Number of results
        """
        # Get text embedding
        text_emb = self.embed_text(text_query)
        
        # Calculate similarities
        similarities = np.dot(image_embeddings, text_emb)
        
        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = [
            {'index': int(idx), 'similarity': float(similarities[idx])}
            for idx in top_indices
        ]
        
        return results

# Usage
searcher = MultiModalSearch()

# Index some images
images = [Image.open(f'product_{i}.jpg') for i in range(10)]
embeddings = embedder.embed_batch(images)

# Search with text
results = searcher.search_by_text(
    "comfortable office chair",
    embeddings,
    top_k=3
)

print("Search results:")
for result in results:
    print(f"  Image {result['index']}: {result['similarity']:.3f}")
```

### Similarity Calculation

```python
import numpy as np

def cosine_similarity(emb1, emb2):
    """Calculate cosine similarity between two embeddings"""
    return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

def euclidean_distance(emb1, emb2):
    """Calculate Euclidean distance"""
    return np.linalg.norm(emb1 - emb2)

def find_most_similar(query_emb, candidate_embs, top_k=5, metric='cosine'):
    """
    Find most similar embeddings
    
    Args:
        query_emb: Query embedding (1D array)
        candidate_embs: Candidate embeddings (2D array)
        top_k: Number of results
        metric: 'cosine' or 'euclidean'
    """
    if metric == 'cosine':
        # Cosine similarity (higher is better)
        scores = np.dot(candidate_embs, query_emb)
        top_indices = np.argsort(scores)[::-1][:top_k]
    else:
        # Euclidean distance (lower is better)
        distances = np.linalg.norm(candidate_embs - query_emb, axis=1)
        top_indices = np.argsort(distances)[:top_k]
        scores = -distances  # Invert for consistency
    
    return [
        {'index': int(idx), 'score': float(scores[idx])}
        for idx in top_indices
    ]

# Usage
query = embedder.embed_image(Image.open('query.jpg'))
candidates = embedder.embed_batch([Image.open(f'db_{i}.jpg') for i in range(100)])

similar = find_most_similar(query, candidates, top_k=5)
```

---

## Vector Database Operations

### ChromaDB Setup and Basic Operations

```python
import chromadb
from chromadb.config import Settings
import numpy as np

# Initialize client
client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(anonymized_telemetry=False)
)

# Create collection
collection = client.get_or_create_collection(
    name="product_images",
    metadata={"description": "Product image embeddings"}
)

# Add embeddings
embeddings = [np.random.randn(512).astype(np.float32) for _ in range(10)]
ids = [f"product_{i}" for i in range(10)]
metadatas = [{'category': 'furniture', 'price': 99.99} for _ in range(10)]

collection.add(
    embeddings=[emb.tolist() for emb in embeddings],
    ids=ids,
    metadatas=metadatas
)

# Search
query_embedding = np.random.randn(512).astype(np.float32)

results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=5
)

print(f"Found {len(results['ids'][0])} results")
```

### Advanced Database Operations

```python
class VectorDatabase:
    def __init__(self, persist_dir="./vector_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = None
    
    def create_collection(self, name):
        """Create or get collection"""
        self.collection = self.client.get_or_create_collection(name)
        return self.collection
    
    def bulk_add(self, embeddings, ids=None, metadatas=None, batch_size=100):
        """Add embeddings in batches"""
        if ids is None:
            ids = [str(i) for i in range(len(embeddings))]
        
        for i in range(0, len(embeddings), batch_size):
            batch_embs = embeddings[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size] if metadatas else None
            
            self.collection.add(
                embeddings=[e.tolist() for e in batch_embs],
                ids=batch_ids,
                metadatas=batch_meta
            )
            
            print(f"Added batch {i//batch_size + 1}")
    
    def search_with_filters(self, query_embedding, filters, top_k=5):
        """Search with metadata filters"""
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=filters  # e.g., {'category': 'furniture'}
        )
        
        return results
    
    def update_metadata(self, id, new_metadata):
        """Update metadata for an item"""
        self.collection.update(
            ids=[id],
            metadatas=[new_metadata]
        )
    
    def delete_items(self, ids):
        """Delete items by IDs"""
        self.collection.delete(ids=ids)
    
    def get_stats(self):
        """Get database statistics"""
        return {
            'count': self.collection.count(),
            'name': self.collection.name
        }

# Usage
db = VectorDatabase()
db.create_collection("products")

# Bulk add
embeddings = [np.random.randn(512) for _ in range(1000)]
db.bulk_add(embeddings, batch_size=100)

# Search with filters
query = np.random.randn(512)
results = db.search_with_filters(
    query,
    filters={'category': 'electronics', 'price': {'$lt': 100}},
    top_k=10
)
```

---

## REST API Examples

### Complete FastAPI Server

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io

app = FastAPI(title="Visual Search API")

# Global models (loaded on startup)
detector = None
embedder = None
vector_db = None

@app.on_event("startup")
async def startup():
    global detector, embedder, vector_db
    detector = ObjectDetector()
    embedder = CLIPEmbedder()
    vector_db = VectorDatabase()

@app.post("/api/detect")
async def detect_objects(file: UploadFile = File(...)):
    """Detect objects in image"""
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Detect
        detections = detector.detect_with_filters(image)
        
        return {
            'success': True,
            'count': len(detections),
            'detections': detections
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search_similar(file: UploadFile = File(...), top_k: int = 5):
    """Search for similar images"""
    try:
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Generate embedding
        embedding = embedder.embed_image(image)
        
        # Search database
        results = vector_db.search_with_filters(
            embedding,
            filters={},
            top_k=top_k
        )
        
        return {
            'success': True,
            'results': results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get API statistics"""
    return {
        'database': vector_db.get_stats(),
        'models': {
            'detector': detector is not None,
            'embedder': embedder is not None
        }
    }

# Run with: uvicorn main:app --reload
```

### API Client (Python)

```python
import requests
from pathlib import Path

class VisualSearchClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def detect_objects(self, image_path):
        """Detect objects in image"""
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/api/detect", files=files)
        
        return response.json()
    
    def search_similar(self, image_path, top_k=5):
        """Search for similar images"""
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'top_k': top_k}
            response = requests.post(f"{self.base_url}/api/search", files=files, data=data)
        
        return response.json()
    
    def get_stats(self):
        """Get API stats"""
        response = requests.get(f"{self.base_url}/api/stats")
        return response.json()

# Usage
client = VisualSearchClient()

# Detect objects
result = client.detect_objects('test.jpg')
print(f"Found {result['count']} objects")

# Search similar
results = client.search_similar('query.jpg', top_k=5)
print(f"Found {len(results['results'])} similar images")
```

---

## Frontend Examples

### Streamlit Image Upload

```python
import streamlit as st
from PIL import Image
import requests

st.title("🔍 Visual Search")

# File uploader
uploaded_file = st.file_uploader("Upload image", type=['jpg', 'png'])

if uploaded_file:
    # Display image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    # Detect button
    if st.button("Detect Objects"):
        with st.spinner("Detecting..."):
            # Send to API
            files = {'file': uploaded_file.getvalue()}
            response = requests.post('http://localhost:8000/api/detect', files=files)
            result = response.json()
            
            # Display results
            if result['success']:
                st.success(f"Found {result['count']} objects!")
                
                for det in result['detections']:
                    st.write(f"**{det['class']}** - Confidence: {det['confidence']:.2%}")
```

### React Image Upload Component

```javascript
// ImageUpload.jsx
import React, { useState } from 'react';

function ImageUpload() {
  const [image, setImage] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleDetect = async () => {
    if (!image) return;

    setLoading(true);
    
    const formData = new FormData();
    formData.append('file', image);

    try {
      const response = await fetch('http://localhost:8000/api/detect', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" accept="image/*" onChange={handleImageChange} />
      <button onClick={handleDetect} disabled={loading}>
        {loading ? 'Detecting...' : 'Detect Objects'}
      </button>

      {results && (
        <div>
          <h3>Found {results.count} objects:</h3>
          {results.detections.map((det, i) => (
            <div key={i}>
              {det.class}: {(det.confidence * 100).toFixed(1)}%
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ImageUpload;
```

---

## Model Optimization

### ONNX Export and Inference

```python
import onnx
import onnxruntime as ort

# Export YOLOv8 to ONNX
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
model.export(format='onnx', simplify=True)

# Load and run ONNX model
session = ort.InferenceSession(
    'yolov8n.onnx',
    providers=['CPUExecutionProvider']
)

# Prepare input
input_data = preprocess_image(image)

# Run inference
outputs = session.run(None, {'images': input_data})

# Process outputs
detections = postprocess_yolo_output(outputs)
```

### Model Quantization

```python
from onnxruntime.quantization import quantize_dynamic, QuantType

def quantize_model(input_model, output_model):
    """Quantize ONNX model to INT8"""
    quantize_dynamic(
        model_input=input_model,
        model_output=output_model,
        weight_type=QuantType.QUInt8
    )
    
    print(f"✓ Quantized: {input_model} → {output_model}")

quantize_model('yolov8n.onnx', 'yolov8n_int8.onnx')
```

---

## Data Collection

### Web Scraping with Beautiful Soup

```python
from bs4 import BeautifulSoup
import requests

def scrape_product_images(url):
    """Scrape product images from a webpage"""
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all product images
    images = soup.find_all('img', class_='product-image')
    
    image_urls = []
    for img in images:
        src = img.get('src') or img.get('data-src')
        if src:
            image_urls.append(src)
    
    return image_urls
```

---

**For complete implementation, see the full project files in the repository!**

