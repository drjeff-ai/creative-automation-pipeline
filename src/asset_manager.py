"""
Asset Manager Module

Handles checking existing assets, validating images, and managing file operations.
"""

import requests
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from PIL import Image

logger = logging.getLogger(__name__)


class AssetManager:
    """Manages campaign assets and checks for existing/missing images."""
    
    def __init__(self, asset_folder: str = "input_assets"):
        """
        Initialize AssetManager.
        
        Args:
            asset_folder: Path to folder containing input assets
        """
        self.asset_folder = Path(asset_folder)
        self.asset_folder.mkdir(exist_ok=True)
        logger.info(f"AssetManager initialized with folder: {self.asset_folder}")
    
    def check_existing_assets(self, products: List[Dict]) -> Tuple[Dict, List]:
        """
        Check which product assets exist and which need to be generated.
        
        Args:
            products: List of product dictionaries from campaign brief
            
        Returns:
            Tuple of (existing_assets_dict, missing_products_list)
        """
        existing = {}
        missing = []
        
        logger.info(f"Checking assets for {len(products)} products...")
        
        for product in products:
            product_id = product.get('id')
            if not product_id:
                logger.warning(f"Product missing 'id' field: {product}")
                continue
            
            # Check for common image extensions
            extensions = ['.png', '.jpg', '.jpeg', '.webp']
            found = False
            
            for ext in extensions:
                asset_path = self.asset_folder / f"{product_id}{ext}"
                if asset_path.exists():
                    if self.validate_image(asset_path):
                        existing[product_id] = asset_path
                        logger.info(f"✓ Found existing asset: {asset_path.name}")
                        found = True
                        break
                    else:
                        logger.warning(f"⚠ Invalid image file: {asset_path.name}")
            
            if not found:
                missing.append(product)
                logger.info(f"✗ Missing asset for: {product_id}")
        
        logger.info(f"Summary: {len(existing)} existing, {len(missing)} missing")
        return existing, missing
    
    def validate_image(self, image_path: Path) -> bool:
        """
        Validate that an image file is readable and has correct format.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with Image.open(image_path) as img:
                # Verify image can be loaded
                img.verify()
            
            # Re-open to check actual loading (verify closes the file)
            with Image.open(image_path) as img:
                width, height = img.size
                
                # Basic sanity checks
                if width < 100 or height < 100:
                    logger.warning(f"Image too small: {width}x{height}")
                    return False
                
                if width > 10000 or height > 10000:
                    logger.warning(f"Image too large: {width}x{height}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Image validation failed for {image_path}: {e}")
            return False
    
    def save_generated_image(self, image_url: str, product_id: str) -> Path:
        """
        Download and save a generated image.
        
        Args:
            image_url: URL of generated image
            product_id: Product identifier
            
        Returns:
            Path to saved image
        """
        logger.info(f"Downloading image for {product_id} from {image_url[:50]}...")
        
        try:
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Save to input_assets folder
            save_path = self.asset_folder / f"{product_id}.png"
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            # Validate saved image
            if self.validate_image(save_path):
                logger.info(f"✓ Saved image: {save_path}")
                return save_path
            else:
                logger.error(f"✗ Downloaded image failed validation")
                save_path.unlink()  # Delete invalid file
                raise ValueError("Downloaded image failed validation")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download image: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise
    
    def get_asset_path(self, product_id: str) -> Path:
        """
        Get the path to a product's asset.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Path to asset file
        """
        # Check for existing file with any extension
        extensions = ['.png', '.jpg', '.jpeg', '.webp']
        for ext in extensions:
            path = self.asset_folder / f"{product_id}{ext}"
            if path.exists():
                return path
        
        # Return default .png path even if doesn't exist
        return self.asset_folder / f"{product_id}.png"
