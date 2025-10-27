"""
OpenAI LLM Provider

Wrapper for OpenAI API (GPT-4, GPT-4-turbo, etc.)
"""

import logging
from openai import OpenAI
from .base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
        """
        super().__init__(api_key, model)
        self.client = OpenAI(api_key=api_key)
    
    def generate_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 300
    ) -> str:
        """Generate prompt using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            prompt = response.choices[0].message.content.strip()
            logger.debug(f"OpenAI generated prompt: {prompt[:100]}...")
            return prompt
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "OpenAI"
    
    def get_cost_per_call(self) -> float:
        """Estimated cost per prompt generation."""
        return 0.01  # ~$0.01 per 1k tokens