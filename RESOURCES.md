# Free Resources & Links

Comprehensive list of all free tools, datasets, APIs, and platforms used in this project.

## 🤖 Pre-trained Models

### Object Detection

1. **YOLOv8** (Ultralytics)
   - URL: https://github.com/ultralytics/ultralytics
   - License: AGPL-3.0
   - Models: Nano, Small, Medium, Large, XLarge
   - Download: Auto-downloads via pip

2. **Faster R-CNN** (Alternative)
   - URL: https://pytorch.org/vision/stable/models.html
   - License: BSD
   - Torchvision pre-trained models

3. **EfficientDet** (Alternative)
   - URL: https://github.com/google/automl/tree/master/efficientdet
   - License: Apache 2.0

### Visual Embeddings

1. **CLIP** (OpenAI)
   - URL: https://github.com/openai/CLIP
   - HuggingFace: https://huggingface.co/openai/clip-vit-base-patch32
   - License: MIT
   - Models: ViT-B/32, ViT-B/16, ViT-L/14

2. **DINOv2** (Meta) - Alternative
   - URL: https://github.com/facebookresearch/dinov2
   - License: Apache 2.0
   - Very good for visual similarity

3. **ImageBind** (Meta) - Multi-modal
   - URL: https://github.com/facebookresearch/ImageBind
   - License: MIT
   - Supports image, text, audio, video

---

## 📊 Free Datasets

### General Object Detection

1. **COCO Dataset**
   - URL: https://cocodataset.org/
   - Images: 330K
   - Categories: 80
   - Size: ~25GB
   - License: CC-BY 4.0
   - Download: http://images.cocodataset.org/

2. **Open Images V7**
   - URL: https://storage.googleapis.com/openimages/web/index.html
   - Images: 9M
   - Categories: 600
   - Size: ~500GB (use subset)
   - License: CC-BY 4.0
   - Download: https://storage.googleapis.com/openimages/web/download.html

3. **ImageNet**
   - URL: https://www.image-net.org/
   - Images: 14M
   - Categories: 20K
   - License: Various (check per image)
   - Note: Academic use

### E-commerce & Products

1. **Products-10K**
   - URL: https://github.com/zhanghang1989/PyTorch-Multi-Style-Transfer
   - Images: 10K products
   - License: Research use

2. **DeepFashion2**
   - URL: https://github.com/switchablenorms/DeepFashion2
   - Images: 491K fashion items
   - License: Non-commercial research

3. **Grocery Store Dataset**
   - URL: https://github.com/marcusklasson/GroceryStoreDataset
   - Images: 5K grocery products
   - License: MIT

### Free Image Sources

1. **Unsplash**
   - URL: https://unsplash.com/
   - API: https://unsplash.com/developers
   - Free tier: 50 requests/hour
   - License: Unsplash License (free use)

2. **Pexels**
   - URL: https://www.pexels.com/
   - API: https://www.pexels.com/api/
   - Free tier: 200 requests/hour
   - License: Free for commercial use

3. **Wikimedia Commons**
   - URL: https://commons.wikimedia.org/
   - API: https://www.mediawiki.org/wiki/API
   - License: Various (CC0, CC-BY, CC-BY-SA)

---

## ☁️ Free Cloud Platforms

### Compute & Hosting

1. **Fly.io**
   - URL: https://fly.io
   - Free tier: 3 shared VMs, 3GB storage
   - Best for: API hosting
   - Docs: https://fly.io/docs/

2. **Render**
   - URL: https://render.com
   - Free tier: 750 hours/month
   - Best for: Web services
   - Auto-sleep after 15min

3. **Google Cloud Run**
   - URL: https://cloud.google.com/run
   - Free tier: 2M requests/month
   - Best for: Container apps
   - Docs: https://cloud.google.com/run/docs

4. **Railway**
   - URL: https://railway.app
   - Free tier: $5 credit/month
   - Best for: Quick deploys

5. **Heroku** (Limited)
   - URL: https://www.heroku.com
   - Free tier: Discontinued, but eco dynos available
   - Alternative: Use others above

### GPU Compute (Training)

1. **Google Colab**
   - URL: https://colab.research.google.com/
   - Free GPU: T4 (15GB)
   - Time limit: 12 hours
   - Best for: Model fine-tuning

2. **Kaggle Notebooks**
   - URL: https://www.kaggle.com/
   - Free GPU: P100 (16GB)
   - Time limit: 9 hours/session
   - Best for: Training experiments

3. **Lightning AI**
   - URL: https://lightning.ai
   - Free tier: Limited GPU hours
   - Best for: PyTorch Lightning projects

### Storage

1. **Cloudflare R2**
   - URL: https://www.cloudflare.com/products/r2/
   - Free tier: 10GB storage
   - Best for: Image storage

2. **Backblaze B2**
   - URL: https://www.backblaze.com/b2/cloud-storage.html
   - Free tier: 10GB storage
   - S3-compatible

3. **Supabase Storage**
   - URL: https://supabase.com/storage
   - Free tier: 1GB
   - Best for: User uploads

---

## 🗄️ Free Vector Databases

1. **ChromaDB**
   - URL: https://www.trychroma.com/
   - Type: Embedded (local)
   - License: Apache 2.0
   - Best for: MVP, small-scale
   - Docs: https://docs.trychroma.com/

2. **Milvus Lite**
   - URL: https://milvus.io/
   - Type: Standalone
   - License: Apache 2.0
   - Best for: Medium-scale
   - Docs: https://milvus.io/docs

3. **Weaviate Cloud Free Tier**
   - URL: https://weaviate.io/
   - Free tier: 1 cluster
   - Best for: Production-ready features
   - Docs: https://weaviate.io/developers/weaviate

4. **Pinecone Free Tier**
   - URL: https://www.pinecone.io/
   - Free tier: 1 index, 5M vectors
   - Best for: Managed service
   - Docs: https://docs.pinecone.io/

5. **Qdrant Cloud Free Tier**
   - URL: https://qdrant.tech/
   - Free tier: 1GB cluster
   - Best for: Fast similarity search
   - Docs: https://qdrant.tech/documentation/

---

## 🛠️ Free Development Tools

### API Development

1. **FastAPI**
   - URL: https://fastapi.tiangolo.com/
   - License: MIT
   - Best for: Python APIs

2. **Flask**
   - URL: https://flask.palletsprojects.com/
   - License: BSD
   - Alternative to FastAPI

### Frontend

1. **Streamlit**
   - URL: https://streamlit.io/
   - License: Apache 2.0
   - Best for: Quick MVP
   - Hosting: streamlit.io/cloud (free)

2. **Gradio**
   - URL: https://gradio.app/
   - License: Apache 2.0
   - Alternative to Streamlit
   - Hosting: HuggingFace Spaces (free)

3. **React**
   - URL: https://reactjs.org/
   - License: MIT
   - Best for: Production apps

### Mobile

1. **Flutter**
   - URL: https://flutter.dev/
   - License: BSD
   - Best for: Cross-platform mobile

2. **React Native**
   - URL: https://reactnative.dev/
   - License: MIT
   - Alternative to Flutter

---

## 🔍 Free APIs & Services

### Search & Web Data

1. **SerpAPI** (Limited)
   - URL: https://serpapi.com/
   - Free tier: 100 searches/month
   - Use: Web search results

2. **Custom Search API** (Google)
   - URL: https://developers.google.com/custom-search
   - Free tier: 100 queries/day
   - Use: Image search

### Translation

1. **Deep Translator** (Library)
   - URL: https://pypi.org/project/deep-translator/
   - License: MIT
   - Free: Unlimited

2. **LibreTranslate**
   - URL: https://libretranslate.com/
   - Free tier: 10 req/day
   - Self-hosted: Unlimited

### Image Processing

1. **Pillow**
   - URL: https://python-pillow.org/
   - License: HPND
   - Use: Image manipulation

2. **OpenCV**
   - URL: https://opencv.org/
   - License: Apache 2.0
   - Use: Advanced image processing

---

## 📚 Learning Resources

### Tutorials

1. **YOLOv8 Course** (Free)
   - URL: https://docs.ultralytics.com/
   - Video: https://www.youtube.com/watch?v=m9fH9OWn8YM

2. **CLIP Tutorial** (HuggingFace)
   - URL: https://huggingface.co/docs/transformers/model_doc/clip

3. **FastAPI Tutorial**
   - URL: https://fastapi.tiangolo.com/tutorial/

4. **Vector Databases Guide**
   - URL: https://www.pinecone.io/learn/vector-database/

### Courses

1. **Deep Learning Specialization** (Coursera)
   - URL: https://www.coursera.org/specializations/deep-learning
   - Free to audit

2. **Fast.ai**
   - URL: https://www.fast.ai/
   - Completely free
   - Practical deep learning

3. **Stanford CS231n**
   - URL: http://cs231n.stanford.edu/
   - Free lectures on YouTube

### Books (Free)

1. **Dive into Deep Learning**
   - URL: https://d2l.ai/
   - Topics: CNN, attention, transformers

2. **Neural Networks and Deep Learning**
   - URL: http://neuralnetworksanddeeplearning.com/

---

## 🔧 Free Tools

### Monitoring

1. **Sentry**
   - URL: https://sentry.io/
   - Free tier: 5K events/month
   - Use: Error tracking

2. **Uptime Robot**
   - URL: https://uptimerobot.com/
   - Free tier: 50 monitors
   - Use: Uptime monitoring

### CI/CD

1. **GitHub Actions**
   - URL: https://github.com/features/actions
   - Free tier: 2,000 min/month
   - Use: Automated deployment

2. **GitLab CI**
   - URL: https://docs.gitlab.com/ee/ci/
   - Free tier: 400 min/month

### Analytics

1. **Google Analytics**
   - URL: https://analytics.google.com/
   - Free: Unlimited
   - Use: User tracking

2. **Plausible** (Self-hosted)
   - URL: https://plausible.io/
   - License: AGPL-3.0
   - Privacy-focused

---

## 📖 Papers & Research

### Key Papers

1. **YOLO** (You Only Look Once)
   - v1: https://arxiv.org/abs/1506.02640
   - v8: https://arxiv.org/abs/2305.09972

2. **CLIP** (Contrastive Language-Image Pre-training)
   - URL: https://arxiv.org/abs/2103.00020
   - OpenAI Blog: https://openai.com/blog/clip/

3. **Vision Transformer (ViT)**
   - URL: https://arxiv.org/abs/2010.11929

4. **DINOv2**
   - URL: https://arxiv.org/abs/2304.07193

### Research Platforms

1. **Papers with Code**
   - URL: https://paperswithcode.com/
   - Free implementations of papers

2. **arXiv**
   - URL: https://arxiv.org/
   - Free research papers

---

## 🤝 Community & Support

### Forums

1. **Stack Overflow**
   - URL: https://stackoverflow.com/
   - Tags: pytorch, yolo, clip, fastapi

2. **Reddit**
   - r/MachineLearning
   - r/computervision
   - r/learnmachinelearning

3. **Discord Servers**
   - PyTorch: https://discord.gg/pytorch
   - Ultralytics: https://discord.gg/ultralytics

### GitHub Topics

- https://github.com/topics/visual-search
- https://github.com/topics/image-similarity
- https://github.com/topics/object-detection

---

## 💡 Alternative Tools

If you want to try different approaches:

### Object Detection
- Detectron2 (Facebook)
- MMDetection (OpenMMLab)
- TensorFlow Object Detection API

### Embeddings
- ResNet features
- EfficientNet
- MobileNet (lighter)

### Vector DB
- FAISS (Facebook)
- Annoy (Spotify)
- NMSLIB

### Frameworks
- TensorFlow + Keras
- JAX + Flax
- ONNX Runtime

---

## 📝 License Summary

| Component | License | Commercial Use |
|-----------|---------|----------------|
| YOLOv8 | AGPL-3.0 | Yes (with restrictions) |
| CLIP | MIT | Yes |
| ChromaDB | Apache 2.0 | Yes |
| FastAPI | MIT | Yes |
| Streamlit | Apache 2.0 | Yes |
| COCO Dataset | CC-BY 4.0 | Yes (with attribution) |

**Always check individual licenses before commercial use!**

---

## 🎯 Quick Links

- **Models**: [Ultralytics](https://github.com/ultralytics/ultralytics), [HuggingFace](https://huggingface.co/)
- **Datasets**: [COCO](https://cocodataset.org/), [Open Images](https://storage.googleapis.com/openimages/web/index.html)
- **Cloud**: [Fly.io](https://fly.io), [Render](https://render.com)
- **GPU**: [Google Colab](https://colab.research.google.com/), [Kaggle](https://www.kaggle.com/)
- **Docs**: [FastAPI](https://fastapi.tiangolo.com/), [Streamlit](https://docs.streamlit.io/)

---

**All resources listed are free for personal and/or commercial use (with noted restrictions). Always verify current terms and pricing.**

Last updated: October 2025

