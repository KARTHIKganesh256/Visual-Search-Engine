"""
YOLOv8 Object Detector
Detects objects in images using pre-trained YOLOv8 models
"""

from ultralytics import YOLO
import numpy as np
from PIL import Image
import torch
from pathlib import Path
from typing import List, Dict

# Fix for PyTorch 2.6 weights_only issue
from .pytorch_fix import apply_pytorch_fix
apply_pytorch_fix()


class ObjectDetector:
    """
    Object detection using YOLOv8
    
    Model sizes:
    - 'n' (nano): Fastest, smallest (6MB)
    - 's' (small): Balanced (22MB)
    - 'm' (medium): More accurate (52MB)
    - 'l' (large): High accuracy (88MB)
    - 'x' (xlarge): Best accuracy (136MB)
    """
    
    def __init__(
        self,
        model_size: str = 'n',
        confidence_threshold: float = 0.25,
        image_size: int = 768,
        use_tta: bool = True
    ):
        """
        Initialize YOLOv8 detector
        
        Args:
            model_size: Model size ('n', 's', 'm', 'l', 'x')
            confidence_threshold: Minimum confidence for detections
            image_size: Inference image size (pixels)
            use_tta: Enable light test-time augmentation for accuracy
        """
        self.model_size = model_size
        self.confidence_threshold = confidence_threshold
        self.image_size = image_size
        self.use_tta = use_tta
        
        # Use GPU if available
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Load model (auto-downloads if not present)
        model_name = f'yolov8{model_size}.pt'
        self.model = YOLO(model_name)
        try:
            self.model.fuse()
        except Exception:
            # Fuse may fail on some backends; ignore
            pass
        
        print(f"✓ YOLOv8-{model_size} loaded on {self.device}")
        print(f"  Model supports {len(self.model.names)} classes")
    
    def detect(self, image: Image.Image, return_crops: bool = False) -> List[Dict]:
        """
        Detect objects in image
        
        Args:
            image: PIL Image
            return_crops: Whether to return cropped object images
            
        Returns:
            List of detections with class, confidence, and bbox
        """
        # Run inference
        results = self.model.predict(
            image,
            conf=self.confidence_threshold,
            device=self.device,
            imgsz=self.image_size,
            augment=self.use_tta,
            verbose=False
        )
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            
            for i, box in enumerate(boxes):
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Get class and confidence
                cls_id = int(box.cls[0].cpu().numpy())
                confidence = float(box.conf[0].cpu().numpy())
                class_name = self.model.names[cls_id]
                
                detection = {
                    'class': class_name,
                    'class_id': cls_id,
                    'confidence': confidence,
                    'bbox': [float(x1), float(y1), float(x2), float(y2)]
                }
                
                # Optionally crop object region
                if return_crops:
                    crop = image.crop((x1, y1, x2, y2))
                    detection['crop'] = crop
                
                detections.append(detection)
        
        return detections
    
    def detect_batch(self, images: List[Image.Image]) -> List[List[Dict]]:
        """
        Detect objects in batch of images (faster)
        
        Args:
            images: List of PIL Images
            
        Returns:
            List of detection lists for each image
        """
        results = self.model(images, conf=self.confidence_threshold, device=self.device)
        
        all_detections = []
        
        for result in results:
            detections = []
            boxes = result.boxes
            
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cls_id = int(box.cls[0].cpu().numpy())
                confidence = float(box.conf[0].cpu().numpy())
                
                detections.append({
                    'class': self.model.names[cls_id],
                    'class_id': cls_id,
                    'confidence': confidence,
                    'bbox': [float(x1), float(y1), float(x2), float(y2)]
                })
            
            all_detections.append(detections)
        
        return all_detections
    
    def get_dominant_object(self, image: Image.Image) -> Dict:
        """
        Get the most prominent object in image
        (largest bounding box area)
        
        Args:
            image: PIL Image
            
        Returns:
            Dominant object detection or None
        """
        detections = self.detect(image)
        
        if not detections:
            return None
        
        # Find largest by area
        def bbox_area(det):
            x1, y1, x2, y2 = det['bbox']
            return (x2 - x1) * (y2 - y1)
        
        return max(detections, key=bbox_area)
    
    def export_onnx(self, output_path: str = None):
        """
        Export model to ONNX format for faster inference
        
        Args:
            output_path: Path to save ONNX model
        """
        if output_path is None:
            output_path = f'yolov8{self.model_size}.onnx'
        
        self.model.export(format='onnx', simplify=True)
        print(f"✓ Model exported to {output_path}")
        print("  Use with onnxruntime for faster CPU inference")


# Example usage and testing
if __name__ == "__main__":
    import requests
    from io import BytesIO
    
    # Initialize detector
    detector = ObjectDetector(model_size='n')
    
    # Test on sample image
    print("\nTesting on sample image...")
    url = "https://ultralytics.com/images/bus.jpg"
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    
    # Detect objects
    detections = detector.detect(image)
    
    print(f"\nFound {len(detections)} objects:")
    for det in detections:
        print(f"  - {det['class']}: {det['confidence']:.2f}")
    
    # Get dominant object
    dominant = detector.get_dominant_object(image)
    if dominant:
        print(f"\nDominant object: {dominant['class']} ({dominant['confidence']:.2f})")

