"""
Flux Image Provider

Wrapper for Flux Pro 1.1 via fal.ai
"""

import logging
import os
import time
from typing import Optional
import fal_client
from .base import ImageProvider

logger = logging.getLogger(__name__)


class FluxProvider(ImageProvider):
    """Flux Pro 1.1 provider via fal.ai."""
    
    def __init__(self, api_key: str, model: str = "fal-ai/flux-pro/v1.1"):
        """
        Initialize Flux provider.
        
        Args:
            api_key: fal.ai API key
            model: Model identifier
        """
        super().__init__(api_key, model)
        os.environ["FAL_KEY"] = api_key
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1920,
        height: int = 1080,
        **kwargs
    ) -> str:
        """
        Generate image using Flux Pro.
        
        Args:
            prompt: Image generation prompt
            negative_prompt: Things to avoid
            width: Image width (used to determine aspect ratio)
            height: Image height (used to determine aspect ratio)
            **kwargs: Additional Flux-specific parameters
                - image_size: Flux size preset (overrides width/height)
                - num_inference_steps: Quality steps (default 28)
                - guidance_scale: Prompt adherence (default 3.5)
            
        Returns:
            URL of generated image
        """
        # Get image_size from kwargs (should always be provided now)
        image_size = kwargs.get('image_size')
        if not image_size:
            # Fallback: determine from dimensions
            aspect_ratio = width / height
            if 0.9 <= aspect_ratio <= 1.1:
                image_size = "square"
            elif aspect_ratio > 1.5:
                image_size = "landscape_16_9"
            elif aspect_ratio < 0.7:
                image_size = "portrait_16_9"
            else:
                image_size = "square"
        
        # Use default negative prompt if not provided
        if negative_prompt is None:
            from src.constants import Defaults
            negative_prompt = Defaults.DEFAULT_NEGATIVE_PROMPT
        
        # Flux-specific parameters
        num_inference_steps = kwargs.get('num_inference_steps', 28)
        guidance_scale = kwargs.get('guidance_scale', 3.5)
        
        try:
            start_time = time.time()
            logger.info(f"Generating with Flux Pro: {image_size}")
            
            result = fal_client.subscribe(
                self.model,
                arguments={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "image_size": image_size,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "num_images": 1,
                    "safety_tolerance": "2",
                    "enable_safety_checker": True
                }
            )
            
            generation_time = time.time() - start_time
            
            if result and 'images' in result and len(result['images']) > 0:
                image_url = result['images'][0]['url']
                logger.info(f"✓ Image generated in {generation_time:.2f}s")
                return image_url
            else:
                raise ValueError("No image returned from Flux API")
        
        except Exception as e:
            logger.error(f"Flux API error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "Flux Pro"
    
    def get_cost_per_image(self) -> float:
        """Estimated cost per image."""
        return 0.055  # ~$0.055 per Flux Pro generation