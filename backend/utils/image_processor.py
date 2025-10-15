"""
Image preprocessing utilities
Handles image validation, resizing, and format conversion
"""

from PIL import Image
import io
import numpy as np
from typing import Union, Tuple


class ImageProcessor:
    """
    Image preprocessing for ML models
    
    Handles:
    - Format conversion
    - Resizing
    - Validation
    - Optimization
    """
    
    def __init__(
        self,
        max_size: int = 1024,
        min_size: int = 32,
        target_format: str = 'RGB'
    ):
        """
        Initialize image processor
        
        Args:
            max_size: Maximum dimension (width or height)
            min_size: Minimum dimension
            target_format: Target color format ('RGB', 'L', etc.)
        """
        self.max_size = max_size
        self.min_size = min_size
        self.target_format = target_format
    
    def preprocess(self, image_input: Union[bytes, Image.Image]) -> Image.Image:
        """
        Preprocess image for ML inference
        
        Args:
            image_input: Image bytes or PIL Image
            
        Returns:
            Processed PIL Image
        """
        # Load image if bytes
        if isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
        else:
            image = image_input
        
        # Convert to target format
        if image.mode != self.target_format:
            image = image.convert(self.target_format)
        
        # Validate size
        width, height = image.size
        
        if width < self.min_size or height < self.min_size:
            raise ValueError(f"Image too small: {width}x{height}. Minimum: {self.min_size}px")
        
        # Resize if too large
        if width > self.max_size or height > self.max_size:
            image = self.resize_keep_aspect(image, self.max_size)
        
        return image
    
    @staticmethod
    def resize_keep_aspect(image: Image.Image, max_size: int) -> Image.Image:
        """
        Resize image keeping aspect ratio
        
        Args:
            image: PIL Image
            max_size: Maximum dimension
            
        Returns:
            Resized image
        """
        width, height = image.size
        
        # Calculate new size
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        
        # Resize with high-quality resampling
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def compress(self, image: Image.Image, quality: int = 85) -> bytes:
        """
        Compress image to JPEG bytes
        
        Args:
            image: PIL Image
            quality: JPEG quality (1-100)
            
        Returns:
            Compressed image bytes
        """
        buffer = io.BytesIO()
        
        # Convert to RGB if needed (JPEG doesn't support RGBA)
        if image.mode in ('RGBA', 'LA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image
        
        image.save(buffer, format='JPEG', quality=quality, optimize=True)
        return buffer.getvalue()
    
    def validate_image(self, image_bytes: bytes) -> bool:
        """
        Validate if bytes represent a valid image
        
        Args:
            image_bytes: Image bytes
            
        Returns:
            True if valid, False otherwise
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()
            return True
        except:
            return False
    
    def get_image_info(self, image: Union[bytes, Image.Image]) -> dict:
        """
        Get image metadata
        
        Args:
            image: Image bytes or PIL Image
            
        Returns:
            Dict with image info
        """
        if isinstance(image, bytes):
            img = Image.open(io.BytesIO(image))
        else:
            img = image
        
        return {
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'width': img.width,
            'height': img.height
        }
    
    def center_crop(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """
        Center crop image to specified size
        
        Args:
            image: PIL Image
            size: (width, height) tuple
            
        Returns:
            Cropped image
        """
        width, height = image.size
        target_width, target_height = size
        
        left = (width - target_width) // 2
        top = (height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        return image.crop((left, top, right, bottom))
    
    def augment(self, image: Image.Image, operations: list = None) -> Image.Image:
        """
        Apply data augmentation
        
        Args:
            image: PIL Image
            operations: List of operations to apply
            
        Returns:
            Augmented image
        """
        if operations is None:
            operations = []
        
        for op in operations:
            if op == 'flip_horizontal':
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            elif op == 'flip_vertical':
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
            elif op == 'rotate_90':
                image = image.transpose(Image.ROTATE_90)
            elif op == 'rotate_180':
                image = image.transpose(Image.ROTATE_180)
            elif op == 'rotate_270':
                image = image.transpose(Image.ROTATE_270)
        
        return image
    
    @staticmethod
    def to_numpy(image: Image.Image) -> np.ndarray:
        """
        Convert PIL Image to numpy array
        
        Args:
            image: PIL Image
            
        Returns:
            Numpy array (H, W, C)
        """
        return np.array(image)
    
    @staticmethod
    def from_numpy(array: np.ndarray) -> Image.Image:
        """
        Convert numpy array to PIL Image
        
        Args:
            array: Numpy array (H, W, C)
            
        Returns:
            PIL Image
        """
        # Ensure uint8
        if array.dtype != np.uint8:
            array = (array * 255).astype(np.uint8)
        
        return Image.fromarray(array)


# Example usage
if __name__ == "__main__":
    import requests
    
    # Initialize processor
    processor = ImageProcessor(max_size=512)
    
    # Test with online image
    print("Downloading test image...")
    url = "https://ultralytics.com/images/bus.jpg"
    response = requests.get(url)
    image_bytes = response.content
    
    # Preprocess
    print("\nPreprocessing image...")
    image = processor.preprocess(image_bytes)
    print(f"Processed size: {image.size}")
    
    # Get info
    info = processor.get_image_info(image)
    print("\nImage info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Compress
    compressed = processor.compress(image, quality=75)
    print(f"\nOriginal size: {len(image_bytes)} bytes")
    print(f"Compressed size: {len(compressed)} bytes")
    print(f"Compression ratio: {len(compressed)/len(image_bytes):.2%}")
    
    # Validate
    is_valid = processor.validate_image(compressed)
    print(f"\nCompressed image valid: {is_valid}")

