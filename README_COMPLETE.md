# 🔍 Complete Visual Search Engine

A full-stack Visual Search Engine built with **FastAPI** (backend) and **React** (frontend) that uses **ResNet50** for image feature extraction and similarity search.

## ✨ Features

### Backend (FastAPI)
- **Image Indexing**: Upload images with metadata and extract ResNet50 features
- **Similarity Search**: Find similar images using cosine similarity
- **Multiple Input Formats**: Support for file upload and base64 encoding
- **RESTful API**: Clean endpoints with automatic Swagger documentation
- **In-Memory Storage**: Fast access with proper data structures

### Frontend (React + Tailwind)
- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Image Upload**: Drag & drop or click to select images
- **Real-time Preview**: See selected images before processing
- **Search Results**: Display similarity scores and metadata
- **Animations**: Smooth transitions with Framer Motion
- **Statistics**: Live stats about indexed images

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/API    ┌─────────────────┐
│   React Frontend│ ◄────────────► │  FastAPI Backend│
│                 │                │                 │
│ • Image Upload  │                │ • ResNet50      │
│ • Search UI     │                │ • Feature Extr. │
│ • Results Disp. │                │ • Similarity    │
└─────────────────┘                └─────────────────┘
```

## 🚀 Quick Start

### 1. Setup Dependencies

```bash
# Install Python dependencies
pip install fastapi uvicorn python-multipart torch torchvision pillow numpy pydantic python-dotenv

# Install Node.js dependencies
cd frontend
npm install
cd ..
```

### 2. Start the Backend

```bash
python backend/main_complete.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/

### 3. Start the Frontend

```bash
cd frontend
npm start
```

The React app will open at: http://localhost:3000

## 📡 API Endpoints

### Index Image
```http
POST /index
Content-Type: multipart/form-data

file: [image file]
name: "Cat"
```

**Response:**
```json
{
  "id": "uuid-string",
  "name": "Cat", 
  "status": "indexed",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Search Similar Images
```http
POST /search
Content-Type: multipart/form-data

file: [image file]
top_k: 3
```

**Response:**
```json
{
  "results": [
    {
      "name": "Cat",
      "similarity": 0.92,
      "id": "uuid-string"
    }
  ]
}
```

### Get Statistics
```http
GET /stats
```

**Response:**
```json
{
  "total_images": 5,
  "indexed_images": [
    {
      "id": "uuid",
      "name": "Cat",
      "timestamp": "2024-01-01T12:00:00",
      "image_size": [640, 480]
    }
  ]
}
```

### Clear All Data
```http
DELETE /clear
```

## 🎯 Usage Example

1. **Index an Image:**
   - Upload a cat image
   - Enter name "Cat"
   - Click "Index Image"
   - See confirmation: "Image indexed successfully as Cat"

2. **Search Similar Images:**
   - Upload another cat image
   - Click "Search Similar Images"
   - See results with similarity scores

3. **View Results:**
   ```
   Search Results:
   ┌─────────────────┬──────────────┐
   │ Name            │ Similarity   │
   ├─────────────────┼──────────────┤
   │ Cat             │ 92.3%        │
   └─────────────────┴──────────────┘
   ```

## 🔧 Technical Details

### Backend Architecture
- **FastAPI**: Modern, fast web framework
- **ResNet50**: Pre-trained CNN for feature extraction
- **PyTorch**: Deep learning framework
- **Pydantic**: Data validation and serialization
- **In-Memory Storage**: Fast access using Python lists/dicts

### Frontend Architecture
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations
- **Axios**: HTTP client for API calls
- **shadcn/ui**: Beautiful UI components

### Feature Extraction Process
1. **Image Preprocessing**: Resize, normalize, convert to tensor
2. **ResNet50 Forward Pass**: Extract 2048-dimensional features
3. **Feature Normalization**: L2 normalization for cosine similarity
4. **Storage**: Store features with metadata in memory

### Similarity Search Process
1. **Query Processing**: Extract features from query image
2. **Cosine Similarity**: Compute similarity with all stored features
3. **Ranking**: Sort by similarity score (descending)
4. **Top-K Results**: Return most similar images

## 📁 Project Structure

```
visual-search-engine/
├── backend/
│   └── main_complete.py          # Complete FastAPI backend
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main React component
│   │   ├── components/ui/       # UI components (Button, Card, etc.)
│   │   ├── lib/utils.ts         # Utility functions
│   │   └── index.tsx           # React entry point
│   ├── package.json            # Node.js dependencies
│   └── tailwind.config.js      # Tailwind configuration
├── setup_complete.py           # Setup script
└── README_COMPLETE.md         # This file
```

## 🎨 UI Components

### Index Image Card
- Image upload area with drag & drop
- Text input for image name
- Index button with loading state
- Success/error messages

### Search Image Card
- Image upload for search query
- Search button with loading state
- Results display with similarity scores
- Animated result cards

### Statistics Dashboard
- Total images count
- Indexed images list
- Model information
- Clear all button

## 🔒 Error Handling

### Backend Validation
- File type validation (images only)
- Required field validation
- Base64 format validation
- Error responses with detailed messages

### Frontend Error Handling
- Network error handling
- Form validation
- User-friendly error messages
- Loading states for all operations

## 🚀 Performance Optimizations

### Backend
- **Model Caching**: ResNet50 loaded once at startup
- **Feature Normalization**: Pre-computed for fast similarity
- **In-Memory Storage**: No database overhead
- **Async Operations**: Non-blocking I/O

### Frontend
- **Image Compression**: Automatic resizing for uploads
- **Lazy Loading**: Components loaded on demand
- **Memoization**: Prevent unnecessary re-renders
- **Optimistic Updates**: Immediate UI feedback

## 🧪 Testing

### Backend Testing
```bash
# Test health endpoint
curl http://localhost:8000/

# Test image indexing
curl -X POST "http://localhost:8000/index" \
  -F "file=@test_image.jpg" \
  -F "name=Test"

# Test similarity search
curl -X POST "http://localhost:8000/search" \
  -F "file=@query_image.jpg"
```

### Frontend Testing
- Open browser developer tools
- Check network requests in Network tab
- Verify API responses in Console
- Test error scenarios

## 🔧 Configuration

### Backend Configuration
- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 8000
- **Model**: ResNet50 with ImageNet weights
- **Feature Dimension**: 2048
- **Similarity Metric**: Cosine similarity

### Frontend Configuration
- **API Base URL**: http://localhost:8000
- **Max File Size**: Browser default
- **Supported Formats**: All image formats
- **Results Limit**: 3 (configurable)

## 🚀 Deployment

### Production Backend
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn backend.main_complete:app -w 4 -k uvicorn.workers.UvicornWorker

# Or with Docker
docker build -t visual-search-backend .
docker run -p 8000:8000 visual-search-backend
```

### Production Frontend
```bash
# Build for production
cd frontend
npm run build

# Serve with nginx or serve
npx serve -s build -l 3000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **FastAPI** team for the excellent web framework
- **PyTorch** team for the deep learning framework
- **React** team for the frontend library
- **Tailwind CSS** for the utility-first CSS framework
- **shadcn/ui** for the beautiful UI components

---

**Built with ❤️ using modern web technologies**












