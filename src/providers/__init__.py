"""
AI Provider Abstractions

This package provides clean abstractions for LLM and Image generation providers,
making it easy to swap providers without changing core pipeline logic.

Usage:
    from src.providers import OpenAIProvider, FluxProvider
    
    # LLM for prompt engineering
    llm = OpenAIProvider(api_key="sk-...", model="gpt-4")
    prompt = llm.generate_prompt(system_prompt, user_prompt)
    
    # Image generation
    image_gen = FluxProvider(api_key="...", model="fal-ai/flux-pro/v1.1")
    url = image_gen.generate_image(prompt, width=1920, height=1080)

Adding new providers:
    1. Inherit from LLMProvider or ImageProvider
    2. Implement required abstract methods
    3. Import in this file
    
Example:
    # src/providers/anthropic_provider.py
    from .base import LLMProvider
    
    class AnthropicProvider(LLMProvider):
        def generate_prompt(self, system_prompt, user_prompt, **kwargs):
            # Implementation here
            pass
        
        def get_provider_name(self):
            return "Anthropic"
"""

from .base import LLMProvider, ImageProvider
from .openai_provider import OpenAIProvider
from .flux_provider import FluxProvider

__all__ = [
    'LLMProvider',
    'ImageProvider',
    'OpenAIProvider',
    'FluxProvider'
]