# Quick Reference Guide

Fast reference for common tasks and commands.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download models
python scripts/download_models.py

# 3. Start backend (Terminal 1)
cd backend
uvicorn main:app --reload

# 4. Start frontend (Terminal 2)
cd frontend
streamlit run app.py

# 5. Open browser
http://localhost:8501
```

---

## 📝 Common Commands

### Development

```bash
# Run backend
uvicorn backend.main:app --reload --port 8000

# Run frontend
streamlit run frontend/app.py

# Run tests
pytest tests/

# Check code style
flake8 backend/
black backend/ --check
```

### Docker

```bash
# Build image
docker build -t visual-search .

# Run container
docker run -p 8000:8000 visual-search

# Docker compose (if available)
docker-compose up
```

### Deployment

```bash
# Fly.io
fly launch
fly deploy
fly logs
fly status

# Render (via git)
git push origin main  # Auto-deploys
```

---

## 🔧 Configuration

### Environment Variables

```bash
# .env file
PORT=8000
YOLO_MODEL_SIZE=n
CLIP_MODEL=openai/clip-vit-base-patch32
MAX_IMAGE_SIZE=1024
LOG_LEVEL=INFO
```

### Model Selection

```python
# YOLOv8 sizes: 'n', 's', 'm', 'l', 'x'
detector = ObjectDetector(model_size='n')

# CLIP models
embedder = ImageEmbedder('openai/clip-vit-base-patch32')
```

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port availability
netstat -an | grep 8000
```

### Out of memory

```python
# Reduce image size in backend/utils/image_processor.py
max_size = 512  # Instead of 1024

# Use smaller model
detector = ObjectDetector(model_size='n')
```

### Models not downloading

```bash
# Manual download
python scripts/download_models.py

# Check internet connection
ping github.com
```

---

## 📊 API Endpoints

### Health Check
```bash
GET http://localhost:8000/
```

### Detect Objects
```bash
POST http://localhost:8000/detect
Content-Type: multipart/form-data
Body: file=<image>
```

### Search Similar
```bash
POST http://localhost:8000/search
Content-Type: multipart/form-data
Body: file=<image>, top_k=5
```

### Index Image
```bash
POST http://localhost:8000/index
Content-Type: multipart/form-data
Body: file=<image>, metadata=<json>
```

### Statistics
```bash
GET http://localhost:8000/stats
```

---

## 🧪 Testing

### Test API with curl

```bash
# Health check
curl http://localhost:8000/

# Upload image
curl -X POST http://localhost:8000/detect \
  -F "file=@test.jpg"

# Search similar
curl -X POST http://localhost:8000/search \
  -F "file=@query.jpg" \
  -F "top_k=5"
```

### Python client

```python
import requests

# Detect objects
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/detect',
        files={'file': f}
    )
print(response.json())
```

---

## 📦 Data Management

### Add images to database

```python
from backend.ml_models import ImageEmbedder
from backend.database import VectorStore
from PIL import Image

embedder = ImageEmbedder()
vector_store = VectorStore()

image = Image.open('product.jpg')
embedding = embedder.embed(image)

vector_store.add(
    embeddings=[embedding],
    ids=['product_001'],
    metadatas=[{'name': 'Product', 'price': 99.99}]
)
```

### Backup database

```python
# Export to numpy
vector_store.export_to_numpy('backup.npz')

# Import from backup
vector_store.import_from_numpy('backup.npz')
```

---

## 🎨 UI Customization

### Change theme (Streamlit)

```python
# frontend/app.py - Add to st.markdown()
"""
<style>
    .main { background-color: #FFFFFF; }
    h1 { color: #000000; }
</style>
"""
```

---

## ⚡ Performance Tips

### Optimize inference

```python
# Use ONNX
model.export(format='onnx')

# Batch processing
results = detector.detect_batch(images, batch_size=8)

# Cache embeddings
@lru_cache(maxsize=100)
def get_embedding(image_hash):
    return embedder.embed(image)
```

### Reduce memory

```python
# Resize images before processing
image.thumbnail((640, 640))

# Use quantized models
# See OPTIMIZATION.md
```

---

## 📱 Mobile Integration

### Flutter example

```dart
// Upload image
var request = http.MultipartRequest(
  'POST',
  Uri.parse('https://your-api.fly.dev/detect'),
);
request.files.add(
  await http.MultipartFile.fromPath('file', imagePath)
);
var response = await request.send();
```

---

## 🔒 Security

### Add API key authentication

```python
# backend/main.py
from fastapi import Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@app.post("/detect")
async def detect(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(403)
    # ...
```

### Rate limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/detect")
@limiter.limit("10/minute")
async def detect_objects(...):
    # ...
```

---

## 📈 Monitoring

### Check logs

```bash
# Local
tail -f logs/app.log

# Fly.io
fly logs

# Render
# View in dashboard
```

### Add Sentry

```python
import sentry_sdk

sentry_sdk.init(dsn="your-dsn")
```

---

## 🆘 Get Help

### Documentation
- `README.md` - Overview
- `GETTING_STARTED.md` - Setup
- `DEPLOYMENT.md` - Deploy
- `OPTIMIZATION.md` - Optimize
- `CODE_SNIPPETS.md` - Examples

### Links
- YOLOv8: https://docs.ultralytics.com/
- CLIP: https://huggingface.co/openai/clip-vit-base-patch32
- FastAPI: https://fastapi.tiangolo.com/
- Streamlit: https://docs.streamlit.io/

---

## 💡 Pro Tips

1. **Start small**: Use nano model and small dataset
2. **Iterate fast**: Test locally before deploying
3. **Monitor usage**: Track API calls and errors
4. **Cache results**: Speed up repeated queries
5. **Optimize later**: Get it working first

---

**For detailed guides, see full documentation!**

