"""
CLIP Image Embedder
Generates visual embeddings for similarity search
"""

import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
from typing import List, Union

# Fix for PyTorch 2.6 weights_only issue
from .pytorch_fix import apply_pytorch_fix
apply_pytorch_fix()


class ImageEmbedder:
    """
    Generate image embeddings using CLIP
    
    CLIP (Contrastive Language-Image Pre-training) creates embeddings
    that capture visual semantics, enabling similarity search
    """
    
    def __init__(self, model_name: str = 'openai/clip-vit-base-patch32'):
        """
        Initialize CLIP model
        
        Model options (from HuggingFace):
        - 'openai/clip-vit-base-patch32' (149MB, balanced)
        - 'openai/clip-vit-base-patch16' (335MB, more accurate)
        - 'openai/clip-vit-large-patch14' (890MB, best quality)
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        print(f"Loading CLIP model: {model_name}")
        
        # Load model and processor
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        
        # Set to evaluation mode
        self.model.eval()
        
        print(f"✓ CLIP model loaded on {self.device}")
        print(f"  Embedding dimension: {self.model.config.projection_dim}")
    
    def embed(self, image: Union[Image.Image, List[Image.Image]]) -> np.ndarray:
        """
        Generate embedding(s) for image(s)
        
        Args:
            image: Single PIL Image or list of PIL Images
            
        Returns:
            Normalized embedding vector(s) as numpy array
            - Single image: (embedding_dim,)
            - Multiple images: (num_images, embedding_dim)
        """
        # Handle single vs batch
        is_single = not isinstance(image, list)
        if is_single:
            image = [image]
        
        # Process images
        inputs = self.processor(images=image, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate embeddings
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            
            # Normalize embeddings (for cosine similarity)
            image_features = F.normalize(image_features, p=2, dim=-1)
        
        # Convert to numpy
        embeddings = image_features.cpu().numpy()
        
        # Return single embedding if single image was provided
        if is_single:
            return embeddings[0]
        return embeddings
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embedding(s) for text query(ies)
        Enables text-to-image search
        
        Args:
            text: Single text string or list of strings
            
        Returns:
            Normalized text embedding(s)
        """
        is_single = not isinstance(text, list)
        if is_single:
            text = [text]
        
        # Process text
        inputs = self.processor(text=text, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate embeddings
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            text_features = F.normalize(text_features, p=2, dim=-1)
        
        embeddings = text_features.cpu().numpy()
        
        if is_single:
            return embeddings[0]
        return embeddings
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        # Ensure normalized
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Cosine similarity (dot product of normalized vectors)
        similarity = np.dot(embedding1, embedding2)
        
        # Convert from [-1, 1] to [0, 1]
        return (similarity + 1) / 2
    
    def find_similar(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: np.ndarray,
        top_k: int = 5
    ) -> List[tuple]:
        """
        Find most similar embeddings
        
        Args:
            query_embedding: Query embedding (embedding_dim,)
            candidate_embeddings: Candidates (num_candidates, embedding_dim)
            top_k: Number of results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        # Calculate similarities
        similarities = np.dot(candidate_embeddings, query_embedding)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return indices and scores
        results = [(int(idx), float(similarities[idx])) for idx in top_indices]
        return results
    
    def export_onnx(self, output_path: str = "clip_model.onnx"):
        """
        Export vision model to ONNX for faster inference
        
        Args:
            output_path: Path to save ONNX model
        """
        # Create dummy input
        dummy_image = Image.new('RGB', (224, 224))
        inputs = self.processor(images=dummy_image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Export
        torch.onnx.export(
            self.model.vision_model,
            (inputs['pixel_values'],),
            output_path,
            input_names=['pixel_values'],
            output_names=['image_embeds'],
            dynamic_axes={
                'pixel_values': {0: 'batch_size'},
                'image_embeds': {0: 'batch_size'}
            },
            opset_version=14
        )
        
        print(f"✓ CLIP vision model exported to {output_path}")


# Example usage
if __name__ == "__main__":
    import requests
    from io import BytesIO
    
    # Initialize embedder
    embedder = ImageEmbedder()
    
    # Test with sample images
    print("\nTesting image embeddings...")
    
    # Load test images
    urls = [
        "https://ultralytics.com/images/bus.jpg",
        "https://ultralytics.com/images/zidane.jpg"
    ]
    
    images = []
    for url in urls:
        response = requests.get(url)
        images.append(Image.open(BytesIO(response.content)))
    
    # Generate embeddings
    embeddings = embedder.embed(images)
    print(f"Generated embeddings: {embeddings.shape}")
    
    # Test text-to-image
    print("\nTesting text-to-image search...")
    text_queries = ["a photo of a bus", "a photo of a person"]
    
    for query in text_queries:
        text_embed = embedder.embed_text(query)
        
        # Compare with images
        for i, img_embed in enumerate(embeddings):
            sim = embedder.similarity(text_embed, img_embed)
            print(f"  '{query}' vs Image {i+1}: {sim:.3f}")
    
    # Test similarity between images
    print("\nImage-to-image similarity:")
    sim = embedder.similarity(embeddings[0], embeddings[1])
    print(f"  Image 1 vs Image 2: {sim:.3f}")

