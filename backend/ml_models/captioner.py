"""
BLIP Image Captioner
Generates natural-language captions for images.
"""

import os
import ssl
from typing import Optional

import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration


# Disable SSL verification for constrained networks (development only)
os.environ.setdefault('CURL_CA_BUNDLE', '')
os.environ.setdefault('REQUESTS_CA_BUNDLE', '')
ssl._create_default_https_context = ssl._create_unverified_context


class ImageCaptioner:
    """Generate image captions using BLIP.

    Default model: Salesforce/blip-image-captioning-base (~990MB on first pull).
    """

    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base") -> None:
        self.model_name = model_name
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name).to(self.device)
        self.model.eval()

    @torch.inference_mode()
    def caption(self, image: Image.Image, max_new_tokens: int = 20, num_beams: int = 3) -> str:
        """Return a concise caption for the provided image.

        The caption is trimmed to a short phrase suitable as an auto-name.
        """
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        output_ids = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
            length_penalty=0.6,
            no_repeat_ngram_size=2,
        )
        caption: str = self.processor.decode(output_ids[0], skip_special_tokens=True)
        return caption.strip()










