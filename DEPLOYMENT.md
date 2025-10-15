# Deployment Guide

Complete guide for deploying the Visual Search Engine on free cloud platforms.

## 🚀 Quick Deploy Options

### Option 1: Fly.io (Recommended)

**Free Tier**: 3 shared VMs, 3GB persistent storage

#### Prerequisites
```bash
# Install Fly CLI
# Windows (PowerShell)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Mac/Linux
curl -L https://fly.io/install.sh | sh
```

#### Deploy Steps
```bash
# 1. Login to Fly.io
fly auth login

# 2. Create app (first time only)
fly launch
# Choose app name, region, and confirm fly.toml

# 3. Create persistent volume
fly volumes create visual_search_data --size 1

# 4. Deploy
fly deploy

# 5. Check status
fly status
fly logs

# 6. Open app
fly open
```

#### Configuration
Edit `fly.toml` to adjust:
- Region: `primary_region = "iad"` (change to nearest)
- Memory: `memory_mb = 256` (can increase up to 512MB on free tier)
- Scaling: Auto-start/stop to save resources

#### Troubleshooting Fly.io
```bash
# Check logs
fly logs

# SSH into VM
fly ssh console

# Restart
fly apps restart visual-search-engine

# Monitor resources
fly status
```

---

### Option 2: Render

**Free Tier**: 750 hours/month, auto-sleep after 15min inactivity

#### Deploy Steps
1. **Connect GitHub**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New +" → "Web Service"

2. **Configure Service**
   - Repository: Select your repo
   - Name: `visual-search-engine`
   - Environment: `Docker`
   - Region: Choose nearest
   - Branch: `main`

3. **Settings**
   - Build Command: (auto-detected from Dockerfile)
   - Start Command: (auto-detected)
   - Plan: `Free`

4. **Environment Variables** (optional)
   ```
   PORT=8000
   MAX_IMAGE_SIZE=1024
   LOG_LEVEL=INFO
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build (5-10 minutes first time)
   - Get URL: `https://your-app.onrender.com`

#### Auto-Deploy
- Enable "Auto-Deploy" in settings
- Every push to `main` triggers deployment

#### Render Free Tier Limits
- Sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- 750 hours/month total runtime

---

### Option 3: Google Cloud Run

**Free Tier**: 2M requests/month, 360K GB-seconds

#### Prerequisites
```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

#### Deploy Steps
```bash
# 1. Build and push container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/visual-search

# 2. Deploy to Cloud Run
gcloud run deploy visual-search \
  --image gcr.io/YOUR_PROJECT_ID/visual-search \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1

# 3. Get URL
gcloud run services describe visual-search --region us-central1
```

---

### Option 4: Railway

**Free Tier**: $5 credit/month (limited runtime)

#### Deploy Steps
1. Visit [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Connect repository
5. Railway auto-detects Dockerfile
6. Click "Deploy"

---

## 🌐 Frontend Deployment

### Streamlit Cloud (Free)

**Best for:** MVP demo and testing

#### Steps
1. Visit [streamlit.io/cloud](https://streamlit.io/cloud)
2. Sign in with GitHub
3. Click "New app"
4. Select:
   - Repository
   - Branch: `main`
   - Main file: `frontend/app.py`
5. Advanced settings:
   ```
   Python version: 3.10
   ```
6. Update `frontend/app.py`:
   ```python
   # Change API_URL to your deployed backend
   API_URL = "https://your-backend.fly.dev"
   ```
7. Deploy

---

### GitHub Pages + React (Alternative)

For a static frontend:

```bash
# Build React app
cd frontend-react
npm run build

# Deploy to GitHub Pages
npm install -g gh-pages
gh-pages -d build
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file (not in production, use platform settings):

```bash
# API Configuration
PORT=8000
HOST=0.0.0.0

# Model Settings
YOLO_MODEL_SIZE=n  # n, s, m, l, x
CLIP_MODEL=openai/clip-vit-base-patch32
MAX_IMAGE_SIZE=1024

# Database
CHROMA_PERSIST_DIR=./data/chroma

# Performance
MAX_WORKERS=1
BATCH_SIZE=1

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# Security (add in production)
API_KEY=your-secret-key
ALLOWED_ORIGINS=https://your-frontend.com
```

### Platform-Specific Settings

#### Fly.io
Add to `fly.toml`:
```toml
[env]
  YOLO_MODEL_SIZE = "n"
  MAX_IMAGE_SIZE = "512"  # Reduce for faster processing
```

#### Render
Add in dashboard under "Environment":
```
YOLO_MODEL_SIZE=n
MAX_IMAGE_SIZE=512
```

---

## 📊 Monitoring

### Fly.io Monitoring
```bash
# Real-time logs
fly logs

# Metrics
fly dashboard

# Status
fly status
```

### Render Monitoring
- View logs in dashboard
- Metrics tab shows:
  - CPU usage
  - Memory usage
  - Request count

### Add Custom Monitoring

Install Sentry (free tier):
```bash
pip install sentry-sdk
```

In `backend/main.py`:
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1
)
```

---

## 🔒 Security

### Production Checklist

1. **CORS Configuration**
   ```python
   # backend/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend.com"],  # Specific origins
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

2. **Rate Limiting**
   ```bash
   pip install slowapi
   ```
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/detect")
   @limiter.limit("10/minute")
   async def detect_objects(...):
       ...
   ```

3. **API Key Authentication**
   ```python
   from fastapi import Security, HTTPException
   from fastapi.security import APIKeyHeader
   
   api_key_header = APIKeyHeader(name="X-API-Key")
   
   async def verify_api_key(api_key: str = Security(api_key_header)):
       if api_key != os.getenv("API_KEY"):
           raise HTTPException(status_code=403)
   ```

4. **HTTPS Only**
   - Fly.io: Automatic
   - Render: Automatic
   - Custom domain: Add SSL certificate

---

## 💰 Cost Optimization

### Stay Within Free Tiers

1. **Model Size**
   - Use YOLOv8-nano (`n`) - fastest, smallest
   - Use CLIP-base (not large)

2. **Image Size**
   - Limit to 512-1024px max
   - Client-side compression

3. **Caching**
   - Add Redis (free tier: Upstash)
   - Cache embeddings for common images

4. **Auto-Scaling**
   - Fly.io: Enable auto-stop/start
   - Render: Embrace sleep (for hobby projects)

5. **Cold Start Optimization**
   ```python
   # Lazy load models
   detector = None
   
   def get_detector():
       global detector
       if detector is None:
           detector = ObjectDetector()
       return detector
   ```

---

## 🔄 CI/CD Setup

### GitHub Actions (Free)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: superfly/flyctl-actions/setup-flyctl@master
      
      - name: Deploy to Fly.io
        run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Add `FLY_API_TOKEN` to GitHub secrets:
```bash
# Get token
fly auth token

# Add to GitHub: Settings → Secrets → Actions → New secret
# Name: FLY_API_TOKEN
# Value: <your-token>
```

---

## 🧪 Testing Deployment

### Local Testing
```bash
# Test with Docker locally
docker build -t visual-search .
docker run -p 8000:8000 visual-search

# Test API
curl http://localhost:8000/
```

### Production Testing
```bash
# Health check
curl https://your-app.fly.dev/

# Upload test
curl -X POST https://your-app.fly.dev/detect \
  -F "file=@test_image.jpg"
```

---

## 📈 Scaling Path

### When You Outgrow Free Tier

1. **Immediate** (still cheap)
   - Fly.io: Upgrade to shared-cpu-1x ($1.94/month)
   - Add more memory: 512MB → 1GB
   - Persistent volume: 3GB → 10GB

2. **Growing** ($10-50/month)
   - Fly.io: 2-3 VMs for redundancy
   - Upgrade to dedicated CPU
   - Add Redis cache
   - CDN for images (Cloudflare free)

3. **Production** ($50-200/month)
   - Dedicated VMs
   - Distributed vector DB (Milvus cluster)
   - Load balancer
   - Monitoring (Datadog/New Relic)

---

## 🆘 Troubleshooting

### Out of Memory
```toml
# fly.toml
[[vm]]
  memory_mb = 512  # Increase from 256
```

### Slow Cold Starts
- Use model quantization (ONNX)
- Reduce model size
- Enable model caching

### Build Failures
```bash
# Check Dockerfile locally
docker build -t test .

# View build logs
fly logs
```

### Connection Timeouts
- Increase health check timeout
- Optimize model loading
- Add request timeout limits

---

## 📞 Support

- Fly.io: [community.fly.io](https://community.fly.io)
- Render: [community.render.com](https://community.render.com)
- GitHub Issues: [Report bugs](https://github.com/your-repo/issues)

---

**Next Steps:**
1. Choose deployment platform
2. Follow platform-specific guide above
3. Test deployment
4. Set up monitoring
5. Configure custom domain (optional)

