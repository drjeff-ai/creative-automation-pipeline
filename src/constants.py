"""
Constants Module

Centralized definitions for aspect ratios, dimensions, and other constants.
Single source of truth to avoid duplication across the codebase.
"""

from typing import Dict, Tuple


# =============================================================================
# ASPECT RATIOS & DIMENSIONS
# =============================================================================

class AspectRatios:
    """
    Centralized aspect ratio definitions.
    
    Format names are user-facing (used in campaign briefs).
    Dimensions are in pixels (width, height).
    """
    
    # Social media standard formats
    SQUARE = "1x1"
    PORTRAIT_STORY = "9x16"
    LANDSCAPE_FEED = "16x9"
    
    # Dimension mappings for output/composition
    OUTPUT_DIMENSIONS: Dict[str, Tuple[int, int]] = {
        "1x1": (1080, 1080),      # Instagram feed, Twitter
        "9x16": (1080, 1920),     # Instagram/TikTok stories
        "16x9": (1920, 1080),     # YouTube thumbnail, Facebook feed
        "4x5": (1080, 1350),      # Instagram portrait
        "2x3": (1080, 1620),      # Pinterest
    }
    
    # Dimension mappings for generation (may differ from output)
    GENERATION_DIMENSIONS: Dict[str, Tuple[int, int]] = {
        "1x1": (1024, 1024),      # Square
        "9x16": (1080, 1920),     # Portrait story
        "16x9": (1920, 1080),     # Landscape feed
        "4x3": (1024, 768),       # Landscape 4:3
        "3x4": (768, 1024),       # Portrait 3:4
    }
    
    # Flux API format strings (provider-specific)
    FLUX_FORMATS: Dict[str, str] = {
        "1x1": "square",
        "9x16": "portrait_16_9",
        "16x9": "landscape_16_9",
        "4x3": "landscape_4_3",
        "3x4": "portrait_3_4",
    }
    
    @classmethod
    def get_output_size(cls, format_name: str) -> Tuple[int, int]:
        """
        Get output dimensions for a format.
        
        Args:
            format_name: Format like "1x1", "9x16", etc.
            
        Returns:
            (width, height) tuple
        """
        return cls.OUTPUT_DIMENSIONS.get(format_name, (1080, 1080))
    
    @classmethod
    def get_generation_size(cls, format_name: str) -> Tuple[int, int]:
        """
        Get generation dimensions for a format.
        
        Args:
            format_name: Format like "1x1", "9x16", etc.
            
        Returns:
            (width, height) tuple
        """
        return cls.GENERATION_DIMENSIONS.get(format_name, (1920, 1080))
    
    @classmethod
    def get_flux_format(cls, format_name: str) -> str:
        """
        Get Flux API format string for a format.
        
        Args:
            format_name: Format like "1x1", "9x16", etc.
            
        Returns:
            Flux format string like "square", "portrait_16_9"
        """
        return cls.FLUX_FORMATS.get(format_name, "landscape_16_9")
    
    @classmethod
    def all_formats(cls) -> list:
        """Get list of all supported formats."""
        return list(cls.OUTPUT_DIMENSIONS.keys())


# =============================================================================
# API COSTS
# =============================================================================

class APICosts:
    """Estimated API costs in USD."""
    
    OPENAI_GPT4_PER_1K_TOKENS = 0.01
    ANTHROPIC_CLAUDE_PER_1K_TOKENS = 0.015
    
    FLUX_PRO_PER_IMAGE = 0.055
    DALLE3_HD_PER_IMAGE = 0.08
    STABLE_DIFFUSION_PER_IMAGE = 0.02


# =============================================================================
# FILE PATHS
# =============================================================================

class Paths:
    """Standard file paths and folders."""
    
    INPUT_ASSETS = "input_assets"
    INPUT_BRAND = "input_assets/brand"
    INPUT_FONTS = "input_assets/fonts"
    INPUT_TEMPLATES = "input_assets/templates"
    
    OUTPUTS = "outputs"
    CAMPAIGN_BRIEFS = "campaign_briefs"


# =============================================================================
# DEFAULTS
# =============================================================================

class Defaults:
    """Default values for various operations."""
    
    # Image generation
    DEFAULT_ASPECT_RATIO = "16x9"
    DEFAULT_GUIDANCE_SCALE = 3.5
    DEFAULT_INFERENCE_STEPS = 28
    
    # Text overlay
    DEFAULT_FONT_SIZE_RATIO = 0.08  # 8% of smaller dimension
    DEFAULT_TEXT_COLOR = "#FFFFFF"
    DEFAULT_TEXT_POSITION = "bottom"
    
    # Logo
    DEFAULT_LOGO_SCALE = 0.12  # 12% of image width
    DEFAULT_LOGO_POSITION = "top-right"
    
    # Negative prompt for image generation
    DEFAULT_NEGATIVE_PROMPT = (
        "blurry, low quality, distorted, deformed, ugly, "
        "bad anatomy, watermark, text overlay, signature, "
        "amateur, grainy, pixelated, out of focus, "
        "cluttered background, messy, unprofessional"
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'AspectRatios',
    'APICosts',
    'Paths',
    'Defaults',
]