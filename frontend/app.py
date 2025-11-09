"""
Streamlit Frontend for Visual Search Engine
Simple, beautiful UI with camera support
"""

import streamlit as st
import requests
from PIL import Image
import io
import json
import hashlib
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

if "camera_enabled" not in st.session_state:
    st.session_state.camera_enabled = False
if "camera_photo" not in st.session_state:
    st.session_state.camera_photo = None

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
    files = {'file': ('upload.jpg', image_file, 'image/jpeg')}
    response = requests.post(f"{API_URL}/detect", files=files)
    return response.json()


def search_similar(image_file, top_k=5):
    """Search for similar images"""
    files = {'file': ('upload.jpg', image_file, 'image/jpeg')}
    data = {'top_k': top_k}
    response = requests.post(f"{API_URL}/search", files=files, data=data)
    return response.json()


def index_image(image_file, metadata):
    """Add image to vector database"""
    files = {'file': ('upload.jpg', image_file, 'image/jpeg')}
    data = {'metadata': json.dumps(metadata)}
    response = requests.post(f"{API_URL}/index", files=files, data=data)
    return response.json()


def generate_caption(image_file):
    """Generate caption for image"""
    files = {'file': ('upload.jpg', image_file, 'image/jpeg')}
    response = requests.post(f"{API_URL}/caption", files=files)
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

    cam_toggle_col1, cam_toggle_col2 = st.columns(2)
    with cam_toggle_col1:
        if st.button("📷 Turn Camera On", type="primary", disabled=st.session_state.camera_enabled):
            st.session_state.camera_enabled = True
    with cam_toggle_col2:
        if st.button("✖️ Turn Camera Off", disabled=not st.session_state.camera_enabled):
            st.session_state.camera_enabled = False
            st.session_state.camera_photo = None

    camera_placeholder = st.empty()
    camera_photo = None

    if st.session_state.camera_enabled:
        camera_photo = camera_placeholder.camera_input(
            "Take a photo",
            key="camera_input",
            help="Use your camera to capture an image"
        )
        if camera_photo is not None:
            st.session_state.camera_photo = camera_photo
    elif st.session_state.camera_photo:
        camera_placeholder.success("Using last captured photo. Turn the camera on to take a new one.")
    else:
        camera_placeholder.info("Camera is off. Click 'Turn Camera On' to activate.")

    if st.session_state.camera_enabled and st.session_state.camera_photo:
        image_source = st.session_state.camera_photo
    elif uploaded_file:
        image_source = uploaded_file
    else:
        image_source = st.session_state.camera_photo

# Prepare bytes and hash for downstream features
if image_source:
    image_bytes = image_source.getvalue()
    image_hash = hashlib.md5(image_bytes).hexdigest()
    st.session_state["current_image_hash"] = image_hash
else:
    image_bytes = None
    image_hash = None

with col2:
    if image_source:
        st.image(image_source, caption="Input Image", use_column_width=True)
        if 'auto_caption' in st.session_state and st.session_state.get("caption_hash") == image_hash:
            caption_text = st.session_state.get("auto_caption")
            if caption_text:
                st.markdown(f"**Auto Caption:** _{caption_text}_")
        if 'last_detections' in st.session_state and st.session_state.get("last_detection_hash") == image_hash:
            detections = st.session_state.get("last_detections", [])
            if detections:
                tags = sorted({det['class_name'] for det in detections})
                tag_badges = " ".join([f"`{tag}`" for tag in tags])
                st.markdown(f"**Auto Tags:** {tag_badges}")
        if st.session_state.get("auto_category") and st.session_state.get("auto_category_score") is not None and st.session_state.get("last_detection_hash") == image_hash:
            top_name = st.session_state.get("auto_category")
            top_score = st.session_state.get("auto_category_score") or 0.0
            st.markdown(f"**Top Category:** {top_name} ({top_score:.1%})")
        if st.session_state.get("auto_description") and st.session_state.get("metadata_hash") == image_hash:
            st.markdown(f"**Auto Description:** {st.session_state.get('auto_description')}")

# Process image
if image_source and api_status and image_bytes:
    st.markdown("---")
    
    if st.session_state.get("caption_hash") != image_hash:
        with st.spinner("Generating auto caption..."):
            try:
                caption_result = generate_caption(image_bytes)
                caption_text = caption_result.get("caption") if caption_result.get("success", True) else caption_result.get("caption", "")
            except Exception:
                caption_text = ""
        st.session_state["auto_caption"] = caption_text
        st.session_state["caption_hash"] = image_hash
    
    if st.session_state.get("last_detection_hash") != image_hash:
        with st.spinner("Detecting objects for metadata..."):
            try:
                result = detect_objects(image_bytes)
                if result.get('success', True):
                    detections = result.get('detections', [])
                    st.session_state["last_detections"] = detections
                    st.session_state["last_detection_hash"] = image_hash

                    if detections:
                        top_detection = max(detections, key=lambda d: d.get('confidence', 0))
                        st.session_state["auto_category"] = top_detection.get("class_name", "")
                        st.session_state["auto_category_score"] = top_detection.get("confidence", 0.0)
                        auto_tags = sorted({det['class_name'] for det in detections})
                        st.session_state["auto_tags"] = auto_tags

                        caption_base = (st.session_state.get("auto_caption") or "").strip()
                        tag_text = ", ".join(auto_tags)
                        description = caption_base
                        if tag_text:
                            description = f"{description} Detected: {tag_text}.".strip() if description else f"Detected: {tag_text}."
                        st.session_state["auto_description"] = description
                    else:
                        st.session_state["auto_category"] = ""
                        st.session_state["auto_category_score"] = None
                        st.session_state["auto_tags"] = []
                        st.session_state["auto_description"] = st.session_state.get("auto_caption", "")
                else:
                    st.session_state["last_detections"] = []
                    st.session_state["last_detection_hash"] = image_hash
                    st.session_state["auto_category"] = ""
                    st.session_state["auto_category_score"] = None
                    st.session_state["auto_tags"] = []
                    st.session_state["auto_description"] = st.session_state.get("auto_caption", "")
            except Exception:
                st.warning("Object detection is currently unavailable for auto metadata.")
                st.session_state["last_detections"] = []
                st.session_state["last_detection_hash"] = image_hash
                st.session_state["auto_category"] = ""
                st.session_state["auto_category_score"] = None
                st.session_state["auto_tags"] = []
                st.session_state["auto_description"] = st.session_state.get("auto_caption", "")
        # refresh metadata hash so auto description shows
        st.session_state["metadata_hash"] = None

    # MODE 1: Object Detection
    if "Object Detection" in mode:
        st.subheader("🎯 Detected Objects")
        
        detections = st.session_state.get("last_detections", []) if st.session_state.get("last_detection_hash") == image_hash else []
        if detections:
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
            st.info("No objects detected yet. Try uploading a different angle or brighter photo.")
    
    # MODE 2: Similarity Search
    elif "Similarity Search" in mode:
        st.subheader("🎯 Similar Images")
        
        with st.spinner("Searching for similar images..."):
            try:
                result = search_similar(image_bytes, top_k=top_k)
                
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
        
        if image_hash and st.session_state.get("metadata_hash") != image_hash:
            st.session_state["object_name_input"] = st.session_state.get("auto_caption", "")
            st.session_state["category_input"] = st.session_state.get("auto_category", "")
            st.session_state["source_input"] = ""
            st.session_state["price_input"] = ""
            st.session_state["description_input"] = st.session_state.get("auto_description", "")
            st.session_state["metadata_hash"] = image_hash

        # Metadata input
        with st.form("index_form"):
            st.markdown("#### Image Metadata")
            
            col1, col2 = st.columns(2)
            
            with col1:
                object_name = st.text_input(
                    "Object Name",
                    placeholder="e.g., Blue Chair",
                    key="object_name_input",
                )
                category = st.text_input(
                    "Category",
                    placeholder="e.g., Furniture",
                    key="category_input",
                )
            
            with col2:
                source = st.text_input(
                    "Source",
                    placeholder="e.g., IKEA",
                    key="source_input",
                )
                price = st.text_input(
                    "Price (optional)",
                    placeholder="e.g., $99.99",
                    key="price_input",
                )
            
            description = st.text_area(
                "Description (optional)",
                placeholder="Additional details...",
                key="description_input",
            )
            
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
                        
                        result = index_image(image_bytes, metadata)
                        
                        if result['success']:
                            st.success(f"✅ Image indexed successfully!")
                            st.code(f"Image ID: {result['image_id']}")
                            st.session_state["metadata_hash"] = None
                            st.session_state["object_name_input"] = ""
                            st.session_state["category_input"] = ""
                            st.session_state["source_input"] = ""
                            st.session_state["price_input"] = ""
                            st.session_state["description_input"] = ""
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

