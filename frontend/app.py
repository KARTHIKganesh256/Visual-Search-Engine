"""
Streamlit Frontend for Visual Search Engine
Simple, beautiful UI with camera support
"""

import streamlit as st
import requests
from PIL import Image
import io
import json
from typing import Optional

# Configuration
API_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Visual Search Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for white/black classic theme
st.markdown("""
<style>
    .main {
        background-color: #FFFFFF;
    }
    .stApp {
        background-color: #FFFFFF;
    }
    h1, h2, h3 {
        color: #000000;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    .result-card {
        background-color: #F8F8F8;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
    .detection-box {
        background-color: #000000;
        color: #FFFFFF;
        padding: 10px;
        border-radius: 4px;
        margin: 5px 0;
        font-family: monospace;
    }
    .metric-card {
        background-color: #F0F0F0;
        border-left: 4px solid #000000;
        padding: 15px;
        margin: 10px 0;
    }
    .stButton>button {
        background-color: #000000;
        color: #FFFFFF;
        border: none;
        border-radius: 4px;
        padding: 10px 24px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #333333;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False


def detect_objects(image_file):
    """Send image to API for object detection"""
    files = {'file': image_file}
    response = requests.post(f"{API_URL}/detect", files=files)
    return response.json()


def search_similar(image_file, top_k=5):
    """Search for similar images"""
    files = {'file': image_file}
    data = {'top_k': top_k}
    response = requests.post(f"{API_URL}/search", files=files, data=data)
    return response.json()


def index_image(image_file, metadata):
    """Add image to vector database"""
    files = {'file': image_file}
    data = {'metadata': json.dumps(metadata)}
    response = requests.post(f"{API_URL}/index", files=files, data=data)
    return response.json()


# Sidebar
with st.sidebar:
    st.title("🔍 Visual Search")
    st.markdown("---")
    
    # API status
    api_status = check_api_health()
    status_color = "🟢" if api_status else "🔴"
    status_text = "Online" if api_status else "Offline"
    st.markdown(f"**API Status:** {status_color} {status_text}")
    
    if not api_status:
        st.error("Backend API is not running. Please start it with: `uvicorn main:app --reload`")
    
    st.markdown("---")
    
    # Mode selection
    mode = st.radio(
        "Select Mode",
        ["🔍 Object Detection", "🎯 Similarity Search", "📥 Index Image"],
        help="Choose what you want to do"
    )
    
    st.markdown("---")
    
    # Settings
    st.subheader("⚙️ Settings")
    
    if "Similarity Search" in mode:
        top_k = st.slider("Number of results", 1, 20, 5)
    else:
        top_k = 5
    
    st.markdown("---")
    
    # Info
    st.markdown("""
    ### 📖 About
    This is a free & open-source visual search engine powered by:
    - **YOLOv8** for object detection
    - **CLIP** for visual embeddings
    - **ChromaDB** for similarity search
    
    ### 🚀 Features
    - Real-time object detection
    - Similarity search
    - Image indexing
    - Zero-cost deployment
    """)

# Main content
st.title("🔍 Visual Search Engine")
st.markdown("### Upload an image to detect objects or search for similar items")

# Image input
col1, col2 = st.columns([2, 1])

with col1:
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=['jpg', 'jpeg', 'png'],
        help="Upload an image to analyze"
    )
    
    # Camera input
    camera_photo = st.camera_input("Or take a photo", help="Use your camera")
    
    # Use camera photo if available, otherwise use uploaded file
    image_source = camera_photo if camera_photo else uploaded_file

with col2:
    if image_source:
        st.image(image_source, caption="Input Image", use_container_width=True)

# Process image
if image_source and api_status:
    st.markdown("---")
    
    # Convert to bytes
    image_bytes = image_source.getvalue()
    
    # MODE 1: Object Detection
    if "Object Detection" in mode:
        st.subheader("🎯 Detected Objects")
        
        with st.spinner("Detecting objects..."):
            try:
                # Reset file pointer
                image_source.seek(0)
                result = detect_objects(image_source)
                
                if result['success']:
                    detections = result['detections']
                    
                    if detections:
                        # Display statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3 style='margin:0;'>{len(detections)}</h3>
                                <p style='margin:0;'>Objects Found</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            avg_conf = sum(d['confidence'] for d in detections) / len(detections)
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3 style='margin:0;'>{avg_conf:.1%}</h3>
                                <p style='margin:0;'>Avg Confidence</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            unique_classes = len(set(d['class_name'] for d in detections))
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3 style='margin:0;'>{unique_classes}</h3>
                                <p style='margin:0;'>Unique Classes</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Display detections
                        st.markdown("#### Detection Results")
                        for i, det in enumerate(detections, 1):
                            st.markdown(f"""
                            <div class="detection-box">
                                <strong>#{i} {det['class_name'].upper()}</strong><br>
                                Confidence: {det['confidence']:.1%}<br>
                                BBox: [{det['bbox'][0]:.0f}, {det['bbox'][1]:.0f}, {det['bbox'][2]:.0f}, {det['bbox'][3]:.0f}]
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No objects detected in this image. Try a different image or adjust settings.")
                else:
                    st.error("Detection failed. Please try again.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # MODE 2: Similarity Search
    elif "Similarity Search" in mode:
        st.subheader("🎯 Similar Images")
        
        with st.spinner("Searching for similar images..."):
            try:
                image_source.seek(0)
                result = search_similar(image_source, top_k=top_k)
                
                if result['success']:
                    results = result['results']
                    
                    if results:
                        st.success(f"Found {len(results)} similar images")
                        
                        # Display results in grid
                        cols = st.columns(min(3, len(results)))
                        
                        for i, res in enumerate(results):
                            with cols[i % 3]:
                                st.markdown(f"""
                                <div class="result-card">
                                    <h4>Result #{i+1}</h4>
                                    <p><strong>Similarity:</strong> {res['similarity']:.1%}</p>
                                    <p><strong>ID:</strong> {res['id'][:8]}...</p>
                                    <p><strong>Metadata:</strong></p>
                                    <pre style='font-size:0.8em;'>{json.dumps(res['metadata'], indent=2)}</pre>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No similar images found. Try indexing more images first.")
                else:
                    st.error("Search failed. Please try again.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # MODE 3: Index Image
    elif "Index Image" in mode:
        st.subheader("📥 Add Image to Database")
        
        # Metadata input
        with st.form("index_form"):
            st.markdown("#### Image Metadata")
            
            col1, col2 = st.columns(2)
            
            with col1:
                object_name = st.text_input("Object Name", placeholder="e.g., Blue Chair")
                category = st.text_input("Category", placeholder="e.g., Furniture")
            
            with col2:
                source = st.text_input("Source", placeholder="e.g., IKEA")
                price = st.text_input("Price (optional)", placeholder="e.g., $99.99")
            
            description = st.text_area("Description (optional)", placeholder="Additional details...")
            
            submit = st.form_submit_button("📥 Add to Database")
            
            if submit:
                with st.spinner("Indexing image..."):
                    try:
                        # Prepare metadata
                        metadata = {
                            'object_name': object_name,
                            'category': category,
                            'source': source,
                            'price': price,
                            'description': description
                        }
                        
                        # Remove empty fields
                        metadata = {k: v for k, v in metadata.items() if v}
                        
                        image_source.seek(0)
                        result = index_image(image_source, metadata)
                        
                        if result['success']:
                            st.success(f"✅ Image indexed successfully!")
                            st.code(f"Image ID: {result['image_id']}")
                        else:
                            st.error("Indexing failed. Please try again.")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ using 100% free & open-source tools</p>
    <p style='font-size: 0.9em;'>YOLOv8 • CLIP • ChromaDB • FastAPI • Streamlit</p>
</div>
""", unsafe_allow_html=True)

