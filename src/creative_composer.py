"""
Creative Composer Module

Handles image resizing, text overlay, logo placement, and asset composition.
"""

from pathlib import Path
from typing import Dict, List, Optional
import logging
from PIL import Image, ImageDraw, ImageFont, ImageColor
from src.constants import AspectRatios

logger = logging.getLogger(__name__)


class CreativeComposer:
    """Composes final creative assets with text and branding."""
    
    def __init__(self, brand_config: Dict):
        """
        Initialize CreativeComposer with brand configuration.
        
        Args:
            brand_config: Dictionary with logo_path, colors, fonts
        """
        self.brand_config = brand_config
        self.logo = self._load_logo() if brand_config.get("logo_path") else None
        
        # Parse brand colors
        self.primary_color = brand_config.get("primary_color", "#FF5733")
        self.secondary_color = brand_config.get("secondary_color", "#3498DB")
        self.font_color = brand_config.get("font_color", "#FFFFFF")
        
        logger.info("CreativeComposer initialized")
        if self.logo:
            logger.info(f"  Logo loaded: {brand_config.get('logo_path')}")
        logger.info(f"  Brand colors: {self.primary_color}, {self.secondary_color}")
    
    def _load_logo(self) -> Optional[Image.Image]:
        """Load and resize brand logo."""
        try:
            logo_path = Path(self.brand_config.get("logo_path"))
            if not logo_path.exists():
                logger.warning(f"Logo not found: {logo_path}")
                return None
            
            logo = Image.open(logo_path)
            
            # Ensure logo has transparency
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # Resize logo to reasonable size (max 150px on longest side)
            max_logo_size = 150
            ratio = min(max_logo_size / logo.width, max_logo_size / logo.height)
            new_size = (int(logo.width * ratio), int(logo.height * ratio))
            logo = logo.resize(new_size, Image.Resampling.LANCZOS)
            
            logger.info(f"Logo resized to {new_size}")
            return logo
            
        except Exception as e:
            logger.error(f"Failed to load logo: {e}")
            return None
    
    def create_variations(
        self,
        hero_image_path: Path,
        campaign_message: str,
        product_id: str,
        output_folder: Path,
        ratios: List[str] = None
    ) -> List[Path]:
        """
        Create all aspect ratio variations of the hero image.
        
        Args:
            hero_image_path: Path to hero/base image
            campaign_message: Text to overlay
            product_id: Product identifier for file naming
            output_folder: Where to save variations
            ratios: List of ratio names to generate (defaults to all)
            
        Returns:
            List of paths to generated variations
        """
        if ratios is None:
            ratios = AspectRatios.all_formats()
        
        logger.info(f"Creating {len(ratios)} variations for {product_id}")
        
        try:
            # Load hero image
            hero_image = Image.open(hero_image_path)
            if hero_image.mode != 'RGB':
                hero_image = hero_image.convert('RGB')
            
            # Create output folder for this product
            product_folder = output_folder / product_id
            product_folder.mkdir(parents=True, exist_ok=True)
            
            generated_paths = []
            
            for ratio in ratios:
                logger.info(f"  Creating {ratio} variation...")
                
                # Resize image for this ratio
                resized = self.resize_for_ratio(hero_image.copy(), ratio)
                
                # Add text overlay
                with_text = self.add_text_overlay(resized, campaign_message)
                
                # Add logo if available
                if self.logo:
                    final = self.add_logo_overlay(with_text)
                else:
                    final = with_text
                
                # Save
                output_path = product_folder / f"{ratio}.png"
                final.save(output_path, 'PNG', quality=95)
                generated_paths.append(output_path)
                
                logger.info(f"    ✓ Saved: {output_path.name}")
            
            logger.info(f"✓ Created {len(generated_paths)} variations for {product_id}")
            return generated_paths
            
        except Exception as e:
            logger.error(f"Failed to create variations: {e}")
            raise
    
    def resize_for_ratio(self, image: Image.Image, ratio: str) -> Image.Image:
        """
        Resize/crop image to specific aspect ratio using smart center cropping.
        
        Args:
            image: PIL Image object
            ratio: Ratio name (e.g., "1x1", "9x16")
            
        Returns:
            Resized PIL Image
        """
        target_width, target_height = AspectRatios.get_output_size(ratio)
        target_ratio = target_width / target_height
        current_ratio = image.width / image.height
        
        # Calculate scaling to cover the target size
        if current_ratio > target_ratio:
            # Image is wider - scale by height
            scale = target_height / image.height
            new_width = int(image.width * scale)
            new_height = target_height
        else:
            # Image is taller - scale by width
            scale = target_width / image.width
            new_width = target_width
            new_height = int(image.height * scale)
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center crop to exact dimensions
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        cropped = resized.crop((left, top, right, bottom))
        
        return cropped
    
    def add_text_overlay(
        self, 
        image: Image.Image, 
        text: str, 
        position: str = "bottom"
    ) -> Image.Image:
        """
        Add text overlay to image with semi-transparent background.
        Automatically adjusts font size and wraps text based on image dimensions.
        
        Args:
            image: PIL Image object
            text: Text to overlay
            position: Position ("top", "bottom", "center")
            
        Returns:
            Image with text overlay
        """
        # Create a copy to draw on
        img_with_text = image.copy()
        draw = ImageDraw.Draw(img_with_text, 'RGBA')
        
        # Calculate font size based on both width and height for better aspect ratio handling
        # Use smaller dimension to ensure text fits
        min_dimension = min(image.width, image.height)
        max_text_width = int(image.width * 0.85)  # Text should be max 85% of image width
        
        # Start with a font size based on the smaller dimension
        font_size = int(min_dimension * 0.08)  # 8% of smaller dimension
        
        # Try to load a nice font, fall back to default
        try:
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                "C:\\Windows\\Fonts\\arialbd.ttf",  # Windows
                "/System/Library/Fonts/Helvetica.ttc",  # Mac
            ]
            font = None
            for font_path in font_paths:
                if Path(font_path).exists():
                    font = ImageFont.truetype(font_path, font_size)
                    break
            
            if font is None:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
        
        # Word wrap the text if it's too wide
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_text_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate dimensions for multi-line text
        line_height = int(font_size * 1.3)  # 1.3x spacing between lines
        total_text_height = len(lines) * line_height
        
        # Get max width of all lines
        max_line_width = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            max_line_width = max(max_line_width, line_width)
        
        # Add padding
        padding_x = 30
        padding_y = 25
        bg_width = max_line_width + (padding_x * 2)
        bg_height = total_text_height + (padding_y * 2)
        
        # Calculate position based on aspect ratio
        # For portrait images (9:16), position higher to avoid bottom cutoff
        aspect_ratio = image.width / image.height
        
        if position == "bottom":
            x = (image.width - bg_width) // 2
            # Adjust bottom margin based on aspect ratio
            if aspect_ratio < 0.7:  # Portrait (like 9:16)
                bottom_margin = int(image.height * 0.05)  # 5% from bottom
            else:  # Square or landscape
                bottom_margin = 50
            y = image.height - bg_height - bottom_margin
        elif position == "top":
            x = (image.width - bg_width) // 2
            y = 50
        else:  # center
            x = (image.width - bg_width) // 2
            y = (image.height - bg_height) // 2
        
        # Ensure text box doesn't go off screen
        x = max(20, min(x, image.width - bg_width - 20))
        y = max(20, min(y, image.height - bg_height - 20))
        
        # Draw semi-transparent background
        try:
            bg_color = ImageColor.getrgb(self.primary_color) + (200,)  # Add alpha
        except Exception:
            bg_color = (255, 87, 51, 200)  # Fallback color
        
        draw.rectangle(
            [x, y, x + bg_width, y + bg_height],
            fill=bg_color
        )
        
        # Draw each line of text with shadow and outline
        text_y = y + padding_y
        
        try:
            text_color = ImageColor.getrgb(self.font_color)
        except Exception:
            text_color = (255, 255, 255)  # White fallback
        
        # Shadow and outline colors
        shadow_color = (0, 0, 0, 180)  # Semi-transparent black
        outline_color = (0, 0, 0, 255)  # Solid black outline
        
        for line in lines:
            # Center each line
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            text_x = x + (bg_width - line_width) // 2
            
            # Draw drop shadow (offset by 3px)
            draw.text((text_x + 3, text_y + 3), line, font=font, fill=shadow_color)
            
            # Draw outline (2px thick)
            for offset_x in [-2, -1, 0, 1, 2]:
                for offset_y in [-2, -1, 0, 1, 2]:
                    if offset_x != 0 or offset_y != 0:
                        draw.text(
                            (text_x + offset_x, text_y + offset_y), 
                            line, 
                            font=font, 
                            fill=outline_color
                        )
            
            # Draw main text on top
            draw.text((text_x, text_y), line, font=font, fill=text_color)
            text_y += line_height
        
        return img_with_text
    
    def add_logo_overlay(
        self, 
        image: Image.Image, 
        position: str = "top-right"
    ) -> Image.Image:
        """
        Add logo to image in specified corner.
        
        Args:
            image: PIL Image object
            position: Position for logo (top-right, top-left, bottom-right, bottom-left)
            
        Returns:
            Image with logo overlay
        """
        if not self.logo:
            logger.warning("No logo available to add")
            return image
        
        # Create a copy
        img_with_logo = image.copy()
        
        # Calculate position with padding
        padding = 30
        
        if position == "top-right":
            x = image.width - self.logo.width - padding
            y = padding
        elif position == "top-left":
            x = padding
            y = padding
        elif position == "bottom-right":
            x = image.width - self.logo.width - padding
            y = image.height - self.logo.height - padding
        else:  # bottom-left
            x = padding
            y = image.height - self.logo.height - padding
        
        # Paste logo with transparency
        img_with_logo.paste(self.logo, (x, y), self.logo)
        
        return img_with_logo
    
    def batch_create_variations(
        self,
        hero_images: Dict[str, Path],
        campaign_message: str,
        output_folder: Path,
        ratios: List[str] = None
    ) -> Dict[str, List[Path]]:
        """
        Create variations for multiple products.
        
        Args:
            hero_images: Dictionary mapping product_id to hero image path
            campaign_message: Campaign message to overlay
            output_folder: Base output folder
            ratios: List of ratios to generate
            
        Returns:
            Dictionary mapping product_id to list of generated paths
        """
        logger.info(f"Batch creating variations for {len(hero_images)} products")
        
        results = {}
        for product_id, hero_path in hero_images.items():
            try:
                paths = self.create_variations(
                    hero_path,
                    campaign_message,
                    product_id,
                    output_folder,
                    ratios
                )
                results[product_id] = paths
            except Exception as e:
                logger.error(f"Failed to create variations for {product_id}: {e}")
                results[product_id] = []
        
        return results