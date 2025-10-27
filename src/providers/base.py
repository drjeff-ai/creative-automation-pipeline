"""
Base Provider Classes

Abstract interfaces for LLM and Image generation providers.
This allows easy swapping of AI services without changing core logic.
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers (GPT-4, Claude, Gemini, etc.)."""
    
    def __init__(self, api_key: str, model: str):
        """
        Initialize LLM provider.
        
        Args:
            api_key: API key for the service
            model: Model identifier (e.g., "gpt-4", "claude-3-5-sonnet")
        """
        self.api_key = api_key
        self.model = model
        logger.info(f"Initialized {self.__class__.__name__} with model: {model}")
    
    @abstractmethod
    def generate_prompt(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 300
    ) -> str:
        """
        Generate a prompt using the LLM.
        
        Args:
            system_prompt: System instructions
            user_prompt: User request
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated prompt string
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name (e.g., 'OpenAI', 'Anthropic')."""
        pass


class ImageProvider(ABC):
    """Abstract base class for Image generation providers (Flux, DALL-E, Stable Diffusion, etc.)."""
    
    def __init__(self, api_key: str, model: str):
        """
        Initialize Image provider.
        
        Args:
            api_key: API key for the service
            model: Model identifier (e.g., "flux-pro/v1.1", "dall-e-3")
        """
        self.api_key = api_key
        self.model = model
        logger.info(f"Initialized {self.__class__.__name__} with model: {model}")
    
    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> str:
        """
        Generate an image.
        
        Args:
            prompt: Image generation prompt
            negative_prompt: Things to avoid in generation
            width: Image width in pixels
            height: Image height in pixels
            **kwargs: Provider-specific parameters
            
        Returns:
            URL of generated image
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name (e.g., 'Flux', 'DALL-E')."""
        pass
    
    @abstractmethod
    def get_cost_per_image(self) -> float:
        """Return estimated cost per image in USD."""
        pass