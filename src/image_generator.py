"""
Image Generator Module

Uses image generation providers to create images.
Returns image URLs - downloading/saving is handled by AssetManager.
"""

import os
import logging
from src.providers import FluxProvider, ImageProvider
from src.constants import AspectRatios

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generates images using configurable image generation providers."""
    
    def __init__(self, provider: ImageProvider = None):
        """
        Initialize ImageGenerator with an image provider.
        
        Args:
            provider: ImageProvider instance (defaults to Flux Pro via fal.ai)
        """
        if provider is None:
            # Default to Flux Pro
            api_key = os.getenv("FAL_KEY")
            if not api_key:
                raise ValueError("FAL_KEY not found in environment variables")
            provider = FluxProvider(api_key=api_key, model="fal-ai/flux-pro/v1.1")
        
        self.provider = provider
        logger.info(f"ImageGenerator initialized with {self.provider.get_provider_name()}")
    
    def generate(
        self, 
        prompt: str, 
        image_size: str = "landscape_16_9",
        num_inference_steps: int = 28,
        guidance_scale: float = 3.5,
        negative_prompt: str = None
    ) -> str:
        """
        Generate an image using the configured provider.
        
        Args:
            prompt: Image generation prompt
            image_size: Size preset (landscape_16_9, square, portrait_16_9, etc.)
            num_inference_steps: Number of denoising steps (higher = better quality, slower)
            guidance_scale: How closely to follow the prompt (2-5 recommended)
            negative_prompt: Things to avoid in the generation
            
        Returns:
            URL of generated image
        """
        logger.info(f"Generating image...")
        logger.info(f"  Prompt: {prompt[:100]}...")
        logger.info(f"  Size: {image_size}")
        
        # Get dimensions for the requested format
        width, height = AspectRatios.get_generation_size(image_size)
        flux_format = AspectRatios.get_flux_format(image_size)
        
        try:
            image_url = self.provider.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                image_size=flux_format,  # Flux-specific format string
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
            
            logger.info(f"✓ Image generated")
            logger.info(f"  URL: {image_url[:50]}...")
            return image_url
            
        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            raise
    
    # Convenience aliases for backwards compatibility
    def generate_with_flux(self, *args, **kwargs) -> str:
        """Alias for generate() for backwards compatibility."""
        return self.generate(*args, **kwargs)
    
    def generate_square_image(self, prompt: str) -> str:
        """Generate a square image (optimized for social media)."""
        return self.generate(prompt, image_size="1x1")
    
    def generate_portrait_image(self, prompt: str) -> str:
        """Generate a portrait/vertical image (optimized for stories)."""
        return self.generate(prompt, image_size="9x16")