"""
Prompt Engineer Module

Uses LLM providers to generate optimized image generation prompts from campaign briefs.
"""

import os
from typing import Dict
import logging
from src.providers import OpenAIProvider, LLMProvider

logger = logging.getLogger(__name__)


class PromptEngineer:
    """Generates optimized image prompts using configurable LLM providers."""
    
    def __init__(self, provider: LLMProvider = None):
        """
        Initialize PromptEngineer with an LLM provider.
        
        Args:
            provider: LLMProvider instance (defaults to OpenAI GPT-4)
        """
        if provider is None:
            # Default to OpenAI GPT-4
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            provider = OpenAIProvider(api_key=api_key, model="gpt-4")
        
        self.provider = provider
        logger.info(f"PromptEngineer initialized with {self.provider.get_provider_name()}")
    
    def create_image_prompt(self, campaign_brief: Dict, product: Dict) -> str:
        """
        Generate an optimized image prompt for Flux based on campaign brief and product.
        
        Args:
            campaign_brief: Full campaign brief dictionary
            product: Specific product dictionary
            
        Returns:
            Optimized prompt string for image generation
        """
        logger.info(f"Generating prompt for product: {product.get('name', product.get('id'))}")
        
        try:
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(campaign_brief, product)
            
            prompt = self.provider.generate_prompt(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=300
            )
            
            # Log the generated prompt (truncated for readability)
            logger.info(f"Generated prompt: {prompt[:100]}...")
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to generate prompt: {e}")
            # Fallback to basic prompt
            fallback = self._create_fallback_prompt(product)
            logger.warning(f"Using fallback prompt: {fallback[:100]}...")
            return fallback
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for GPT-4."""
        return """You are an expert creative director specializing in product photography 
and social media advertising. Your specialty is creating detailed image generation prompts 
that produce professional, commercial-quality product visuals.

Your prompts should:
- Focus on professional product photography aesthetics
- Include specific lighting, composition, and styling details
- Incorporate lifestyle elements that resonate with target audiences
- Emphasize high quality, commercial-ready output
- Be optimized for photorealistic AI image generation (like Flux Pro)
- Be concise but detailed (2-3 sentences maximum)

CRITICAL COMPOSITION REQUIREMENTS:
- Use CENTER-FOCUSED composition (products centered in frame)
- Avoid placing subjects on opposite edges or far corners
- Keep important elements within the center 60% of the frame
- Use "centered", "middle of frame", "centrally placed" in your prompts
- This ensures the image crops well to different aspect ratios

Output ONLY the image generation prompt - no explanations, no preamble."""
    
    def _build_user_prompt(self, campaign_brief: Dict, product: Dict) -> str:
        """
        Build the user prompt with campaign and product details.
        
        Args:
            campaign_brief: Full campaign brief
            product: Product details
            
        Returns:
            Formatted user prompt string
        """
        product_name = product.get('name', 'Product')
        product_desc = product.get('description', '')
        campaign_message = campaign_brief.get('campaign_message', '')
        target_audience = campaign_brief.get('target_audience', '')
        region = campaign_brief.get('region', '')
        
        # Build context-rich prompt
        prompt = f"""Create a detailed image generation prompt for professional product photography.

Product: {product_name}
Description: {product_desc}
Campaign Theme: {campaign_message}
Target Audience: {target_audience}
Region/Market: {region}

Generate a prompt that will create a hero product image suitable for social media advertising. 
The image should be photorealistic, professionally lit, and styled appropriately for the target 
audience. Include relevant lifestyle context or setting that resonates with {target_audience}.

IMPORTANT: Use CENTER-FOCUSED composition. Keep all products and important elements in the 
center of the frame (not on edges). This image will be cropped to multiple aspect ratios 
(square, portrait, landscape), so centered composition is critical.

Output only the final image prompt."""
        
        return prompt
    
    def _create_fallback_prompt(self, product: Dict) -> str:
        """
        Create a basic fallback prompt if API fails.
        
        Args:
            product: Product details
            
        Returns:
            Basic prompt string
        """
        product_name = product.get('name', 'Product')
        product_desc = product.get('description', '')
        
        return f"""Professional product photography of {product_name}. {product_desc}. 
Centered composition, product in middle of frame, studio lighting, high quality, 
commercial advertising style, clean white background, sharp focus, detailed, photorealistic."""
    
    def batch_create_prompts(self, campaign_brief: Dict, products: list) -> Dict[str, str]:
        """
        Generate prompts for multiple products.
        
        Args:
            campaign_brief: Campaign brief dictionary
            products: List of product dictionaries
            
        Returns:
            Dictionary mapping product IDs to prompts
        """
        logger.info(f"Batch generating prompts for {len(products)} products")
        
        prompts = {}
        for product in products:
            product_id = product.get('id', 'unknown')
            try:
                prompt = self.create_image_prompt(campaign_brief, product)
                prompts[product_id] = prompt
            except Exception as e:
                logger.error(f"Failed to generate prompt for {product_id}: {e}")
                prompts[product_id] = self._create_fallback_prompt(product)
        
        return prompts