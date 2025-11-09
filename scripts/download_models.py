"""
Download and verify ML models
Run this before first startup to cache models
"""

import os
from pathlib import Path
from ultralytics import YOLO
from transformers import CLIPModel, CLIPProcessor
import torch

# Apply PyTorch 2.6 compatibility fix
try:
    import sys
    sys.path.append('backend')
    from ml_models.pytorch_fix import apply_pytorch_fix
    apply_pytorch_fix()
    print("✓ Applied PyTorch compatibility fix")
except Exception as e:
    print(f"⚠ PyTorch fix not applied: {e}")

def create_directories():
    """Create necessary directories"""
    dirs = [
        'backend/models',
        'data/chroma',
        'logs',
        'test_images'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")

def download_yolo(model_size='n'):
    """
    Download YOLOv8 model

    Args:
        model_size: n (nano), s (small), m (medium), l (large), x (xlarge)
    """
    print(f"\n📦 Downloading YOLOv8-{model_size}...")

    # Workaround for PyTorch 2.6 compatibility
    import torch.serialization
    original_load = torch.load

    def patched_load(*args, **kwargs):
        # Force weights_only=False for YOLO model loading
        kwargs['weights_only'] = False
        return original_load(*args, **kwargs)

    # Temporarily patch torch.load
    torch.load = patched_load

    try:
        model_name = f'yolov8{model_size}.pt'
        model = YOLO(model_name)

        # Verify (avoid accessing deprecated/non-existent attributes like model_path)
        print(f"✓ YOLOv8-{model_size} downloaded successfully")
        try:
            class_count = len(getattr(model, 'names', {}))
            print(f"  Classes: {class_count}")
        except Exception:
            pass

        return model
    finally:
        # Restore original torch.load
        torch.load = original_load

def download_clip(model_name='openai/clip-vit-base-patch32'):
    """
    Download CLIP model
    
    Args:
        model_name: HuggingFace model identifier
    """
    print(f"\n📦 Downloading CLIP model: {model_name}...")
    
    # Download model and processor
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)
    
    print(f"✓ CLIP model downloaded successfully")
    print(f"  Model: {model_name}")
    print(f"  Embedding dimension: {model.config.projection_dim}")
    
    return model, processor

def test_models():
    """Test models with dummy data"""
    print("\n🧪 Testing models...")

    # Test YOLO
    print("\n1. Testing YOLOv8...")

    # Apply the same torch.load patch for testing
    original_load = torch.load

    def patched_load(*args, **kwargs):
        # Force weights_only=False for YOLO model loading
        kwargs['weights_only'] = False
        return original_load(*args, **kwargs)

    # Temporarily patch torch.load
    torch.load = patched_load

    try:
        model = YOLO('yolov8n.pt')

        from PIL import Image
        import numpy as np

        # Create dummy image
        dummy_image = Image.fromarray(np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8))

        results = model(dummy_image, verbose=False)
        print("   ✓ YOLOv8 inference working")
    finally:
        # Restore original torch.load
        torch.load = original_load

    # Test CLIP
    print("\n2. Testing CLIP...")
    clip_model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
    clip_processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')

    inputs = clip_processor(images=dummy_image, return_tensors="pt")

    with torch.no_grad():
        image_features = clip_model.get_image_features(**inputs)

    print("   ✓ CLIP inference working")
    print(f"   Embedding shape: {image_features.shape}")

    print("\n✅ All models working correctly!")

def download_test_images():
    """Download sample test images"""
    print("\n📷 Downloading test images...")
    
    import requests
    
    test_urls = {
        'bus.jpg': 'https://ultralytics.com/images/bus.jpg',
        'zidane.jpg': 'https://ultralytics.com/images/zidane.jpg',
    }
    
    for filename, url in test_urls.items():
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                output_path = f'test_images/{filename}'
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"  ✓ Downloaded: {filename}")
            else:
                print(f"  ✗ Failed to download: {filename}")
        except Exception as e:
            print(f"  ✗ Error downloading {filename}: {str(e)}")

def print_summary():
    """Print summary and next steps"""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print("\n📋 Models Downloaded:")
    print("  • YOLOv8-nano (object detection)")
    print("  • CLIP-base-patch32 (embeddings)")
    
    print("\n📁 Directory Structure:")
    print("  • backend/models/ - Model files")
    print("  • data/chroma/ - Vector database")
    print("  • logs/ - Application logs")
    print("  • test_images/ - Sample images")
    
    print("\n🚀 Next Steps:")
    print("  1. Start backend API:")
    print("     cd backend")
    print("     uvicorn main:app --reload")
    
    print("\n  2. Start frontend (in new terminal):")
    print("     cd frontend")
    print("     streamlit run app.py")
    
    print("\n  3. Open browser:")
    print("     http://localhost:8501")
    
    print("\n💡 Tips:")
    print("  • Check DEPLOYMENT.md for cloud deployment")
    print("  • Check OPTIMIZATION.md for performance tuning")
    print("  • Use test_images/ for testing the API")
    
    print("\n" + "="*60 + "\n")

def main():
    """Main setup function"""
    print("="*60)
    print("Visual Search Engine - Model Download & Setup")
    print("="*60)
    
    try:
        # Create directories
        create_directories()
        
        # Download models
        download_yolo(model_size='n')  # Nano model for MVP
        download_clip()
        
        # Test models
        test_models()
        
        # Download test images
        download_test_images()
        
        # Print summary
        print_summary()
        
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        print("\nTroubleshooting:")
        print("  • Check internet connection")
        print("  • Ensure Python 3.9+ is installed")
        print("  • Run: pip install -r requirements.txt")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

