# Frontend-Backend Connection Documentation

## Overview
This document confirms that the React frontend and FastAPI backend are properly connected and configured.

## Connection Configuration

### Backend (FastAPI) - Port 8000
- **File**: `backend/main.py`
- **URL**: `http://localhost:8000`
- **CORS**: Enabled for all origins (configure for production)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend (React) - Port 3000
- **File**: `frontend/src/App.tsx`
- **API Base URL**: `http://localhost:8000`
- **Proxy**: Configured in `package.json`

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

## API Endpoints & Frontend Integration

### 1. Index Image Endpoint
**Backend**: `POST /index`
- Accepts: `file` (image), `name` (string)
- Returns: `{ id, name, status, timestamp }`

**Frontend**: `App.tsx` line 90
```typescript
axios.post(`${API_BASE_URL}/index`, formData)
```

**Status**: ✅ Connected

---

### 2. Search Similar Images Endpoint
**Backend**: `POST /search`
- Accepts: `file` (image), `top_k` (number)
- Returns: `{ success, results: [{ id, name, similarity }] }`

**Frontend**: `App.tsx` line 132
```typescript
axios.post(`${API_BASE_URL}/search`, formData)
```

**Status**: ✅ Connected

---

### 3. Get Statistics Endpoint
**Backend**: `GET /stats`
- Returns: `{ total_images, indexed_images: [{ id, name, timestamp }] }`

**Frontend**: `App.tsx` line 159
```typescript
axios.get(`${API_BASE_URL}/stats`)
```

**Status**: ✅ Connected

---

### 4. Clear Database Endpoint
**Backend**: `DELETE /clear`
- Returns: `{ success, message }`

**Frontend**: `App.tsx` line 173
```typescript
axios.delete(`${API_BASE_URL}/clear`)
```

**Status**: ✅ Connected

---

### 5. Object Detection Endpoint
**Backend**: `POST /detect`
- Accepts: `file` (image)
- Returns: `{ success, detections: [{ class_name, confidence, bbox }], image_id }`

**Frontend**: Not currently used in UI (available via API)

**Status**: ✅ Available

---

## Data Flow

### Indexing Flow
1. User selects image in frontend
2. User enters image name
3. Frontend sends `POST /index` with file and name
4. Backend:
   - Processes image
   - Generates CLIP embedding
   - Stores in ChromaDB with metadata
   - Returns ID, name, status, timestamp
5. Frontend displays success message

### Search Flow
1. User selects query image
2. Frontend sends `POST /search` with file and top_k=3
3. Backend:
   - Processes image
   - Generates CLIP embedding
   - Searches ChromaDB for similar images
   - Returns top 3 results with names and similarity scores
4. Frontend displays results with similarity percentages

## Response Format Compatibility

### Index Response
✅ **Aligned**
```json
{
  "id": "abc123",
  "name": "My Image",
  "status": "indexed",
  "timestamp": "2025-10-15T..."
}
```

### Search Response
✅ **Aligned**
```json
{
  "success": true,
  "results": [
    {
      "id": "abc123",
      "name": "Similar Image",
      "similarity": 0.95
    }
  ]
}
```

### Stats Response
✅ **Aligned**
```json
{
  "total_images": 10,
  "indexed_images": [
    {
      "id": "abc123",
      "name": "Image 1",
      "timestamp": "2025-10-15T..."
    }
  ]
}
```

## Testing

### Backend Test
Run the test script:
```bash
python test_api.py
```

Expected result: All 5 tests pass

### Frontend Test
1. Start backend: `uvicorn backend.main:app --reload`
2. Start frontend: `cd frontend && npm start`
3. Open browser: `http://localhost:3000`
4. Test indexing and searching images

## Running the Application

### Start Backend
```bash
cd "K:\virtual search engine"
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend
```bash
cd "K:\virtual search engine\frontend"
npm start
```

The frontend will automatically open at `http://localhost:3000` and connect to the backend at `http://localhost:8000`.

## Connection Status: ✅ FULLY CONNECTED

Both frontend and backend are properly configured and all endpoints are aligned with correct request/response formats.









