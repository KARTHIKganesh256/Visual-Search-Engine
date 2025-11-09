# Visual Search Engine MVP - Free & Open Source

A visual search engine similar to CamFind that identifies objects from photos and retrieves relevant information using only free/open-source tools.

## 🎯 Project Overview

This MVP allows users to:
- Upload or capture images
- Detect and classify objects using AI
- Search for similar products/images
- Get relevant information about identified objects

**Built entirely with free tools for zero-budget deployment.**

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │ (Streamlit/React)
│  (Web/Mobile)│
└──────┬──────┘
       │ HTTP/REST
┌──────▼──────┐
│   FastAPI   │ (Backend API)
│   Backend   │
└──────┬──────┘
       │
   ┌───┴────┬──────────┐
   │        │          │
┌──▼──┐  ┌─▼──┐  ┌────▼────┐
│YOLO8│  │CLIP│  │ Vector  │
│Model│  │Model│  │   DB    │
└─────┘  └────┘  │(ChromaDB)│
                 └─────────┘
```

## 🚀 Tech Stack (100% Free)

### Frontend
- **Streamlit** - Quick MVP web interface with camera support
- **Alternative**: React + WebRTC for advanced web app
- **Mobile**: Flutter (for future native apps)

### Backend
- **FastAPI** - Modern Python API framework
- **Uvicorn** - ASGI server

### ML/AI Models
- **YOLOv8** (Ultralytics) - Object detection
- **CLIP** (OpenAI) - Visual embeddings & similarity
- **BLIP** (Salesforce) - Natural-language captions for auto-naming
- **PyTorch/ONNX** - Model inference

### Database
- **ChromaDB** - Free vector database (easier than Milvus for MVP)
- **SQLite** - Metadata storage

### Cloud/Hosting
- **Fly.io** - Free tier (3 VMs, 3GB storage)
- **Render** - Free tier alternative
- **GitHub Pages** - Frontend static hosting (if using React)

### Additional Tools
- **Scrapy** - Web scraping for product data
- **Pillow** - Image processing
- **Deep Translator** - Free translation library

## 📋 Step-by-Step Project Plan

### Phase 1: Setup & Core ML (Week 1-2)
1. ✅ Set up Python environment
2. ✅ Install dependencies
3. ✅ Download pre-trained models (YOLOv8, CLIP)
4. ✅ Test object detection on sample images
5. ✅ Extract visual embeddings

### Phase 2: Backend Development (Week 2-3)
1. ✅ Build FastAPI endpoints
   - `/upload` - Image upload
   - `/detect` - Object detection
   - `/caption` - Image captioning (BLIP)
   - `/search` - Similarity search
2. ✅ Integrate vector database (ChromaDB)
3. ✅ Add preprocessing pipeline
4. ✅ Implement caching

### Phase 3: Frontend Development (Week 3-4)
1. ✅ Build Streamlit interface
2. ✅ Add camera/file upload
3. ✅ Display detection results
4. ✅ Show similar images
5. ✅ Apply white/black classic UI theme

### Phase 4: Data & Training (Week 4-5)
1. ✅ Download free datasets (COCO, Open Images)
2. ✅ Create product database (scrape e-commerce sites)
3. ✅ Generate embeddings for products
4. ✅ Optional: Fine-tune on specific categories

### Phase 5: Deployment (Week 5-6)
1. ✅ Optimize models (quantization)
2. ✅ Deploy on Fly.io/Render
3. ✅ Set up CI/CD with GitHub Actions
4. ✅ Test performance

### Phase 6: Advanced Features (Week 6+)
1. Multi-modal search (text + image)
2. Basic AR integration
3. Offline mode with TensorFlow Lite
4. Social sharing

## 🛠️ Quick Start

### 1. Prerequisites
```bash
# Python 3.9+
python --version

# Git
git --version
```

### 2. Installation
```bash
# Clone repository
git clone <your-repo-url>
cd vritual-scrach-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Download Models (Automatic)
Models are downloaded automatically on first run. Manual download:
```bash
python scripts/download_models.py
```

### 4. Run Backend API
```bash
cd backend
uvicorn main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

Captioning notes:
- First run will download BLIP weights. If behind corporate SSL interception, the code disables SSL verification during model download for development.

### 5. Run Frontend
```bash
cd frontend
streamlit run app.py
```
Open: http://localhost:8501

## 📊 Free Datasets & Resources

### Datasets
1. **COCO Dataset** (330K images, 80 object categories)
   - URL: https://cocodataset.org/
   - Size: ~25GB
   - Use: General object detection

2. **Open Images V7** (9M images, 600 categories)
   - URL: https://storage.googleapis.com/openimages/web/index.html
   - Size: ~500GB (use subset)
   - Use: Diverse everyday objects

3. **ImageNet** (14M images, 20K categories)
   - URL: https://www.image-net.org/
   - Use: Classification training

4. **Products-10K** (10K product images)
   - URL: https://github.com/zhanghang1989/PyTorch-Multi-Style-Transfer
   - Use: E-commerce products

### Free APIs
- **SerpAPI Free Tier** - 100 searches/month
- **Unsplash API** - Free image search
- **WikiMedia Commons** - Open image database

### Tutorials
- YOLOv8: https://docs.ultralytics.com/
- CLIP: https://github.com/openai/CLIP
- FastAPI: https://fastapi.tiangolo.com/
- Streamlit: https://docs.streamlit.io/

## 🎨 UI Design

Classic white & black theme with:
- Minimalist layout
- High contrast for clarity
- Mobile-responsive design
- Accessibility features

## 🚢 Deployment Options

### Option 1: Fly.io (Recommended)
```bash
# Install CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```
**Free tier**: 3 shared VMs, 3GB storage

### Option 2: Render
1. Connect GitHub repo
2. Select "Web Service"
3. Use Docker or Python
4. Deploy (free tier: 750 hours/month)

### Option 3: Google Cloud Run
- 2 million requests/month free
- Container-based deployment

## 💡 Optimization Tips

### Model Optimization
```python
# 1. Quantization (reduce model size by 4x)
# See: backend/ml_models/optimize.py

# 2. Use ONNX Runtime (2-3x faster inference)
# 3. Batch processing for multiple images
# 4. Cache frequent results
```

### Cost Reduction
- Compress images before processing (max 1024px)
- Implement rate limiting
- Use client-side resizing
- Cache embeddings in SQLite

### Performance
- Use async endpoints in FastAPI
- Lazy load models
- Implement request queuing
- Add CDN for static assets (Cloudflare free tier)

## 🔒 Privacy & Security

- **No data retention**: Images deleted after processing
- **Local processing option**: TensorFlow Lite for mobile
- **HTTPS only**: Enforce secure connections
- **Rate limiting**: Prevent abuse

## 📈 Scalability Path

### Short-term (MVP)
- Single server on Fly.io
- ChromaDB in-memory
- ~100 requests/day

### Mid-term (Growth)
- Scale to 3 free Fly.io VMs
- Persistent ChromaDB storage
- CDN for images
- ~1K requests/day

### Long-term (Production)
- Migrate to dedicated hosting
- Kubernetes cluster
- Distributed vector DB
- Model serving on edge
- ~100K+ requests/day

## 🤝 Contributing

This is an open-source MVP project. Contributions welcome!

## 📄 License

MIT License - Free for personal and commercial use

## 🆘 Troubleshooting

### Model download fails
```bash
# Manually download to backend/models/
# YOLOv8: https://github.com/ultralytics/assets/releases
# CLIP: Auto-downloaded via torch hub
```

### Out of memory
```bash
# Reduce image size in config.py
MAX_IMAGE_SIZE = 512  # Default: 1024
```

### ChromaDB errors
```bash
pip install --upgrade chromadb
```

## 🎯 Roadmap

- [x] Core object detection
- [x] Similarity search
- [x] Web interface
- [ ] Mobile app (Flutter)
- [ ] Offline mode
- [ ] AR integration
- [ ] Multi-language support
- [ ] Social features
- [ ] Advanced analytics

## 📞 Support

For issues, please create a GitHub issue or check documentation.

---

**Built with ❤️ using 100% free and open-source tools**

