# Performance Optimization Guide

Complete guide to optimize your Visual Search Engine for speed, accuracy, and cost-efficiency within free-tier limits.

## 🎯 Optimization Goals

1. **Fast inference** (<2 seconds per image)
2. **Low memory usage** (<512MB)
3. **Accurate results** (>80% confidence)
4. **Free-tier friendly** (minimal CPU/storage)

---

## 🚀 Model Optimization

### 1. Model Quantization

Convert models to INT8 (4x smaller, 2-3x faster):

```python
# backend/ml_models/optimize.py

import torch
from ultralytics import YOLO

def quantize_yolo(input_model='yolov8n.pt', output_model='yolov8n_int8.onnx'):
    """
    Quantize YOLOv8 to INT8 ONNX format
    """
    model = YOLO(input_model)
    
    # Export to ONNX with INT8 quantization
    model.export(
        format='onnx',
        dynamic=True,
        simplify=True,
        opset=13
    )
    
    # Further optimize with ONNX Runtime
    import onnxruntime as ort
    from onnxruntime.quantization import quantize_dynamic, QuantType
    
    quantize_dynamic(
        model_input=f'yolov8n.onnx',
        model_output=output_model,
        weight_type=QuantType.QUInt8
    )
    
    print(f"✓ Quantized model saved: {output_model}")

if __name__ == "__main__":
    quantize_yolo()
```

**Run optimization:**
```bash
cd backend/ml_models
python optimize.py
```

**Results:**
- Size: 6MB → 1.5MB (75% reduction)
- Speed: 2-3x faster on CPU
- Accuracy: ~2% loss (acceptable)

---

### 2. Use ONNX Runtime

Faster inference engine:

```bash
pip install onnxruntime
```

```python
# backend/ml_models/detector.py (modified)

import onnxruntime as ort
import numpy as np

class OptimizedDetector:
    def __init__(self, model_path='yolov8n_int8.onnx'):
        # Create ONNX Runtime session
        self.session = ort.InferenceSession(
            model_path,
            providers=['CPUExecutionProvider']
        )
        
    def detect(self, image):
        # Preprocess
        input_data = self.preprocess(image)
        
        # Run inference
        outputs = self.session.run(None, {'images': input_data})
        
        # Postprocess
        return self.postprocess(outputs)
```

**Speed improvement:**
- PyTorch: ~300ms per image
- ONNX: ~100ms per image (3x faster)

---

### 3. Model Selection

Choose the right model for your use case:

#### YOLOv8 Variants

| Model | Size | Speed (CPU) | mAP | Use Case |
|-------|------|-------------|-----|----------|
| nano (n) | 6MB | 100ms | 37.3 | **MVP/Free Tier** |
| small (s) | 22MB | 200ms | 44.9 | Balanced |
| medium (m) | 52MB | 400ms | 50.2 | Better accuracy |
| large (l) | 88MB | 600ms | 52.9 | High accuracy |
| xlarge (x) | 136MB | 900ms | 53.9 | Best quality |

**Recommendation:** Use `nano` for free tier, `small` if you can afford more resources.

#### CLIP Variants

| Model | Size | Embedding Dim | Speed |
|-------|------|---------------|-------|
| clip-vit-base-patch32 | 149MB | 512 | Fast (200ms) ✓ |
| clip-vit-base-patch16 | 335MB | 512 | Medium (400ms) |
| clip-vit-large-patch14 | 890MB | 768 | Slow (800ms) |

**Recommendation:** Use `base-patch32` for MVP.

---

### 4. Lazy Loading

Load models only when needed:

```python
# backend/main.py

class ModelManager:
    def __init__(self):
        self._detector = None
        self._embedder = None
    
    @property
    def detector(self):
        if self._detector is None:
            self._detector = ObjectDetector(model_size='n')
        return self._detector
    
    @property
    def embedder(self):
        if self._embedder is None:
            self._embedder = ImageEmbedder()
        return self._embedder

models = ModelManager()
```

**Benefit:** Faster startup, lower memory when idle

---

## 💾 Database Optimization

### 1. ChromaDB Configuration

```python
# backend/database/vector_store.py

client = chromadb.PersistentClient(
    path=persist_directory,
    settings=Settings(
        # Performance settings
        chroma_db_impl="duckdb+parquet",
        chroma_collection_embedding_dim=512,
        
        # Memory optimization
        anonymized_telemetry=False,
        allow_reset=True
    )
)
```

### 2. Indexing Strategy

```python
# Batch indexing (much faster)
def batch_index(images, batch_size=32):
    embeddings = embedder.embed(images)  # Batch embedding
    
    for i in range(0, len(embeddings), batch_size):
        batch = embeddings[i:i+batch_size]
        vector_store.add(embeddings=batch)
```

### 3. Compression

Store compressed embeddings:

```python
import numpy as np

def compress_embedding(embedding, precision='float16'):
    """Reduce embedding precision"""
    return embedding.astype(np.float16)  # 50% size reduction

def decompress_embedding(compressed):
    """Restore for search"""
    return compressed.astype(np.float32)
```

**Result:** 512 floats × 4 bytes = 2KB → 1KB (50% reduction)

---

## 🖼️ Image Optimization

### 1. Client-Side Compression

```javascript
// frontend/src/utils/imageCompression.js

async function compressImage(file, maxSizeMB = 1, maxWidthOrHeight = 1024) {
    const options = {
        maxSizeMB: maxSizeMB,
        maxWidthOrHeight: maxWidthOrHeight,
        useWebWorker: true
    };
    
    const compressedFile = await imageCompression(file, options);
    return compressedFile;
}
```

**Benefit:** Reduce upload time and server processing

### 2. Server-Side Preprocessing

```python
# backend/utils/image_processor.py

class OptimizedProcessor(ImageProcessor):
    def preprocess(self, image_bytes):
        # Decode
        image = Image.open(io.BytesIO(image_bytes))
        
        # Aggressive resize for free tier
        if image.width > 640 or image.height > 640:
            image = self.resize_keep_aspect(image, max_size=640)
        
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
```

### 3. Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_cached_embedding(image_hash):
    """Cache embeddings for recently processed images"""
    return embedder.embed(image)

# Usage
image_hash = hashlib.md5(image_bytes).hexdigest()
embedding = get_cached_embedding(image_hash)
```

---

## ⚡ API Optimization

### 1. Async Processing

```python
# backend/main.py

import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

@app.post("/detect")
async def detect_objects_async(file: UploadFile):
    image_bytes = await file.read()
    
    # Run CPU-intensive task in thread pool
    loop = asyncio.get_event_loop()
    detections = await loop.run_in_executor(
        executor,
        detector.detect,
        image_bytes
    )
    
    return detections
```

### 2. Request Batching

```python
from collections import deque
import asyncio

class RequestBatcher:
    def __init__(self, max_batch_size=8, max_wait_time=0.1):
        self.queue = deque()
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
    
    async def add_request(self, image):
        future = asyncio.Future()
        self.queue.append((image, future))
        
        if len(self.queue) >= self.max_batch_size:
            await self.process_batch()
        
        return await future
    
    async def process_batch(self):
        if not self.queue:
            return
        
        batch = [self.queue.popleft() for _ in range(min(len(self.queue), self.max_batch_size))]
        images = [item[0] for item in batch]
        
        # Batch inference
        results = detector.detect_batch(images)
        
        # Return results
        for (_, future), result in zip(batch, results):
            future.set_result(result)
```

**Benefit:** 3-5x throughput improvement

### 3. Response Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

---

## 🎯 Accuracy Optimization

### 1. Confidence Thresholding

```python
# Adjust based on your use case
detector = ObjectDetector(
    model_size='n',
    confidence_threshold=0.35  # Higher = fewer false positives
)
```

### 2. Non-Maximum Suppression (NMS)

```python
# Already in YOLOv8, but you can tune it
results = model(image, conf=0.25, iou=0.45)
# iou: Higher = allow more overlapping boxes
```

### 3. Post-Processing Filters

```python
def filter_detections(detections, min_area=100):
    """Remove tiny/unlikely detections"""
    filtered = []
    
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        area = (x2 - x1) * (y2 - y1)
        
        if area >= min_area:
            filtered.append(det)
    
    return filtered
```

### 4. Fine-Tuning (Optional)

Fine-tune on your specific domain:

```python
# Use Google Colab (free GPU)
from ultralytics import YOLO

# Load pre-trained model
model = YOLO('yolov8n.pt')

# Fine-tune on custom data
model.train(
    data='custom_dataset.yaml',
    epochs=50,
    imgsz=640,
    batch=16,
    device=0  # GPU
)
```

**When to fine-tune:**
- Niche objects not in COCO dataset
- Specific style/angle/lighting
- Domain-specific (e.g., medical, fashion)

---

## 💰 Cost Optimization

### 1. Resource Monitoring

```python
import psutil
import time

class ResourceMonitor:
    def __init__(self):
        self.start_time = time.time()
    
    def get_usage(self):
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_mb': psutil.Process().memory_info().rss / 1024 / 1024,
            'uptime_seconds': time.time() - self.start_time
        }

monitor = ResourceMonitor()

@app.get("/metrics")
async def get_metrics():
    return monitor.get_usage()
```

### 2. Auto-Scaling Configuration

**Fly.io:**
```toml
[http_service]
  auto_stop_machines = true  # Stop when idle
  auto_start_machines = true  # Start on request
  min_machines_running = 0    # Scale to zero
```

**Render:**
- Automatically sleeps after 15 minutes
- Wakes on first request (~30s delay)

### 3. Request Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/detect")
@limiter.limit("20/minute")  # Limit abuse
async def detect_objects(...):
    ...
```

---

## 📊 Benchmarking

### Create Benchmark Script

```python
# scripts/benchmark.py

import time
import requests
from PIL import Image
import io

def benchmark_api(image_path, num_requests=10):
    times = []
    
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    for i in range(num_requests):
        start = time.time()
        
        response = requests.post(
            'http://localhost:8000/detect',
            files={'file': ('test.jpg', image_bytes, 'image/jpeg')}
        )
        
        elapsed = time.time() - start
        times.append(elapsed)
        
        print(f"Request {i+1}: {elapsed:.3f}s")
    
    print(f"\nAverage: {sum(times)/len(times):.3f}s")
    print(f"Min: {min(times):.3f}s")
    print(f"Max: {max(times):.3f}s")

if __name__ == "__main__":
    benchmark_api('test_images/bus.jpg')
```

**Run benchmark:**
```bash
python scripts/benchmark.py
```

### Target Performance

| Metric | Free Tier Target | Production Target |
|--------|------------------|-------------------|
| Inference Time | <2 seconds | <500ms |
| Memory Usage | <512MB | <2GB |
| Cold Start | <30 seconds | <5 seconds |
| Throughput | 10 req/min | 100 req/min |

---

## 🔧 Advanced Optimizations

### 1. Model Pruning

Remove unnecessary layers:

```python
import torch
import torch.nn.utils.prune as prune

def prune_model(model, amount=0.3):
    """Remove 30% of least important weights"""
    for module in model.modules():
        if isinstance(module, torch.nn.Conv2d):
            prune.l1_unstructured(module, name='weight', amount=amount)
            prune.remove(module, 'weight')
    
    return model
```

### 2. TensorRT (NVIDIA GPUs only)

For production with GPU:

```bash
pip install nvidia-tensorrt
```

```python
# Export to TensorRT
model.export(format='engine', device=0)
```

**Speed:** 5-10x faster than PyTorch on GPU

### 3. Distributed Processing

For scaling beyond free tier:

```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379')

@app.task
def process_image_task(image_bytes):
    """Process in background worker"""
    return detector.detect(image_bytes)
```

---

## 📈 Monitoring Optimizations

### 1. Performance Logging

```python
import time
from functools import wraps

def timeit(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        
        logger.info(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

@app.post("/detect")
@timeit
async def detect_objects(...):
    ...
```

### 2. Error Tracking

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
)
```

---

## ✅ Optimization Checklist

- [ ] Use YOLOv8-nano (not larger models)
- [ ] Use CLIP-base-patch32 (not large)
- [ ] Convert models to ONNX
- [ ] Quantize models to INT8
- [ ] Enable lazy loading
- [ ] Resize images to max 640-1024px
- [ ] Implement caching
- [ ] Use async endpoints
- [ ] Enable GZIP compression
- [ ] Add rate limiting
- [ ] Configure auto-scaling
- [ ] Monitor resource usage
- [ ] Set up benchmarking
- [ ] Optimize database queries
- [ ] Use batch processing when possible

---

## 🎓 Next Steps

1. **Measure baseline** - Run benchmarks before optimization
2. **Apply optimizations** - Start with model quantization
3. **Measure again** - Compare performance
4. **Iterate** - Focus on biggest bottlenecks
5. **Monitor production** - Track real-world performance

---

**Remember:** Optimization is about trade-offs. For a free-tier MVP:
- **Prioritize:** Speed and cost efficiency
- **Acceptable:** 2-5% accuracy loss
- **Goal:** Functional demo that can scale later

