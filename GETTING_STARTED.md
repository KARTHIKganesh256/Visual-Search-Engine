# Getting Started Guide

Complete step-by-step guide to get your Visual Search Engine running from scratch.

## 🎯 What You'll Build

A fully functional visual search engine that:
- Detects objects in images using YOLOv8
- Finds similar products using CLIP embeddings
- Provides a web interface for users
- Costs $0 to run on free cloud platforms

**Estimated Time**: 2-3 hours for complete setup

---

## ✅ Prerequisites

### Required
- **Python 3.9+** - Check with `python --version`
- **Git** - Check with `git --version`
- **8GB RAM minimum** (for running models locally)
- **5GB free disk space** (for models and data)

### Optional (for deployment)
- Fly.io or Render account (free)
- GitHub account (free)

---

## 📦 Step 1: Installation

### 1.1 Clone Repository

```bash
# Clone the project
git clone <your-repo-url>
cd vritual-scrach-engine

# Or if starting fresh, create directory
mkdir visual-search-engine
cd visual-search-engine
```

### 1.2 Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**This will install:**
- FastAPI (backend framework)
- PyTorch (deep learning)
- Ultralytics (YOLOv8)
- Transformers (CLIP)
- ChromaDB (vector database)
- Streamlit (frontend)
- And more... (~2GB download)

**Installation time**: 10-15 minutes depending on internet speed

---

## 🤖 Step 2: Download Models

Models are automatically downloaded on first run, but you can pre-download:

```bash
python scripts/download_models.py
```

This downloads:
- **YOLOv8-nano** (6MB) - Object detection
- **CLIP-base-patch32** (149MB) - Visual embeddings

**Total**: ~200MB

---

## 🚀 Step 3: Start Backend API

### 3.1 Navigate to Backend

```bash
cd backend
```

### 3.2 Start Server

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Initializing ML models...
✓ Object detector loaded
✓ Image embedder loaded
✓ Vector store initialized
INFO:     All models loaded successfully!
```

### 3.3 Test API

Open browser: http://localhost:8000

You should see:
```json
{
  "status": "online",
  "message": "Visual Search Engine API",
  "version": "1.0.0"
}
```

View API docs: http://localhost:8000/docs

**Keep this terminal open!**

---

## 🎨 Step 4: Start Frontend

### 4.1 Open New Terminal

Activate virtual environment again:

**Windows:**
```powershell
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4.2 Navigate to Frontend

```bash
cd frontend
```

### 4.3 Start Streamlit

```bash
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### 4.4 Open App

Browser should automatically open to: http://localhost:8501

---

## 🧪 Step 5: Test the System

### 5.1 Object Detection

1. Click "Choose an image..." or use camera
2. Upload a test image
3. Select "🔍 Object Detection" mode
4. View results!

**Test Images**: Use images from `test_images/` folder

### 5.2 Add Images to Database

1. Select "📥 Index Image" mode
2. Upload an image
3. Fill in metadata:
   - Object Name: "Blue Office Chair"
   - Category: "Furniture"
   - Source: "Test"
4. Click "Add to Database"

Repeat for 5-10 different images.

### 5.3 Similarity Search

1. Select "🎯 Similarity Search" mode
2. Upload a query image
3. Adjust "Number of results" slider
4. View similar images!

---

## 📊 Step 6: Add More Data

### Option 1: Manual Collection

```bash
# Create data directory
mkdir -p data/products

# Add your own images
# Copy product images to data/products/
```

### Option 2: Use Collection Script

```bash
python scripts/collect_data.py
```

This provides tools to:
- Download from Unsplash (requires free API key)
- Use COCO dataset samples
- Scrape e-commerce sites (responsibly!)

### Option 3: Use Free Datasets

**COCO Dataset** (recommended for MVP):
```bash
# Download subset (adjust URL for specific images)
wget http://images.cocodataset.org/val2017/000000000139.jpg
wget http://images.cocodataset.org/val2017/000000000285.jpg
# ... add to data/products/
```

**Open Images Dataset**:
Visit: https://storage.googleapis.com/openimages/web/index.html
Download specific categories

### Index Your Data

Once you have images, index them:

```python
# index_data.py
from backend.ml_models import ImageEmbedder
from backend.database import VectorStore
from PIL import Image
from pathlib import Path

embedder = ImageEmbedder()
vector_store = VectorStore()

for image_path in Path('data/products').glob('*.jpg'):
    image = Image.open(image_path)
    embedding = embedder.embed(image)
    
    vector_store.add(
        embeddings=[embedding],
        ids=[image_path.stem],
        metadatas=[{'filename': image_path.name}]
    )
    
    print(f"✓ Indexed: {image_path.name}")

print("✅ All images indexed!")
```

Run:
```bash
python index_data.py
```

---

## 🐛 Troubleshooting

### Backend won't start

**Issue**: `ModuleNotFoundError`
```bash
# Make sure you're in virtual environment
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

**Issue**: `CUDA out of memory`
```python
# Edit backend/ml_models/detector.py
# Change device to 'cpu'
self.device = 'cpu'
```

### Frontend shows "API Offline"

1. Check backend is running on port 8000
2. Visit http://localhost:8000 in browser
3. Check firewall isn't blocking port 8000

### Models downloading slowly

Models auto-download on first run. On slow connection:
1. Run `python scripts/download_models.py` separately
2. Wait for completion
3. Then start backend

### Out of memory errors

**Reduce image size**:
```python
# backend/utils/image_processor.py
# Change max_size
max_size = 512  # Instead of 1024
```

**Use smaller model**:
```python
# backend/ml_models/detector.py
# Already using 'n' (nano) - smallest available
```

### ChromaDB errors

```bash
# Upgrade ChromaDB
pip install --upgrade chromadb

# Or delete and recreate database
rm -rf data/chroma
# Restart backend
```

---

## 📈 Next Steps

### 1. Customize for Your Use Case

**Fashion/Clothing**:
- Fine-tune on fashion dataset
- Add color/style filters
- Integrate with shopping APIs

**Home Decor**:
- Focus on furniture detection
- Add room type classification
- Include price range filters

**Food**:
- Use food-specific dataset
- Add nutrition info
- Recipe suggestions

### 2. Improve Accuracy

**Fine-tune models**:
```bash
# Use Google Colab (free GPU)
# See: notebooks/finetune_yolo.ipynb
```

**Add more training data**:
- Collect domain-specific images
- Use data augmentation
- Balance classes

### 3. Add Features

**Multi-modal search**:
```python
# Search with text + image
query_text = "red leather chair"
query_image = Image.open('chair.jpg')

# Combine embeddings
text_emb = embedder.embed_text(query_text)
image_emb = embedder.embed_image(query_image)
combined = (text_emb + image_emb) / 2

results = vector_store.search(combined)
```

**Offline mode**:
```bash
# Export to TensorFlow Lite
pip install tensorflow
# See: scripts/export_tflite.py
```

**AR integration**:
```javascript
// Use AR.js for web-based AR
// See: frontend/ar-demo/
```

### 4. Deploy to Cloud

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides:

**Quick deploy to Fly.io**:
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

**Deploy to Render**:
1. Push to GitHub
2. Connect to Render
3. Select repository
4. Deploy!

### 5. Optimize Performance

See [OPTIMIZATION.md](OPTIMIZATION.md) for:
- Model quantization (4x smaller)
- ONNX conversion (2-3x faster)
- Caching strategies
- Batch processing

---

## 📚 Learning Resources

### YOLOv8
- Documentation: https://docs.ultralytics.com/
- Tutorial: https://www.youtube.com/watch?v=m9fH9OWn8YM
- Paper: https://arxiv.org/abs/2305.09972

### CLIP
- Paper: https://arxiv.org/abs/2103.00020
- Tutorial: https://huggingface.co/docs/transformers/model_doc/clip
- OpenAI Blog: https://openai.com/blog/clip/

### FastAPI
- Documentation: https://fastapi.tiangolo.com/
- Tutorial: https://fastapi.tiangolo.com/tutorial/

### Streamlit
- Documentation: https://docs.streamlit.io/
- Gallery: https://streamlit.io/gallery

### Vector Databases
- ChromaDB: https://docs.trychroma.com/
- Milvus: https://milvus.io/docs
- Pinecone: https://www.pinecone.io/learn/

---

## 🎓 Example Projects

### Similar Open-Source Projects

1. **Image similarity search**: https://github.com/rom1504/clip-retrieval
2. **Product recommendation**: https://github.com/facebookresearch/faiss
3. **Reverse image search**: https://github.com/sethuiyer/Image-Similarity-using-Deep-Learning

### Success Stories

- **Pinterest Visual Search** - Billions of searches/month
- **Google Lens** - Multi-modal search
- **Alibaba Image Search** - E-commerce at scale

### Build Your Portfolio

This project demonstrates:
- ✅ Deep learning (YOLOv8, CLIP)
- ✅ API development (FastAPI)
- ✅ Database design (vector search)
- ✅ Full-stack development
- ✅ Cloud deployment
- ✅ ML optimization

---

## 🤝 Getting Help

### Documentation
- Check README.md for overview
- See CODE_SNIPPETS.md for examples
- Read DEPLOYMENT.md for cloud setup
- Review OPTIMIZATION.md for performance

### Community
- GitHub Issues: Report bugs
- Discussions: Ask questions
- Stack Overflow: Technical help

### Commercial Support
For production deployments:
- Model fine-tuning services
- Cloud architecture consulting
- Performance optimization

---

## ✅ Success Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Models downloaded
- [ ] Backend API running
- [ ] Frontend app running
- [ ] Test image uploaded successfully
- [ ] Object detection working
- [ ] Images indexed to database
- [ ] Similarity search working
- [ ] Ready to customize!

---

## 🎉 You Did It!

Congratulations! You now have a fully functional visual search engine.

**What's next?**
1. Customize for your domain
2. Add more data
3. Deploy to cloud
4. Share with users
5. Iterate and improve!

**Need help?** Open a GitHub issue or check the documentation.

**Want to contribute?** Pull requests are welcome!

---

**Built with ❤️ using 100% free & open-source tools**

Happy building! 🚀

