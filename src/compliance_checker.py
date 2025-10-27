"""
Compliance Checker Module

Handles brand compliance checks and legal content validation.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class ComplianceChecker:
    """Validates brand compliance and legal content requirements."""
    
    # Prohibited marketing terms (customize per industry)
    PROHIBITED_WORDS = [
        "free", "guarantee", "guaranteed", "miracle", "cure", "cures",
        "certified", "approved", "winner", "best", "number one", "#1",
        "risk-free", "no risk", "proven", "scientific breakthrough",
        "secret", "banned", "illegal", "FDA approved"
    ]
    
    def __init__(self, brand_config: Dict = None):
        """
        Initialize ComplianceChecker.
        
        Args:
            brand_config: Dictionary with brand colors, logo path, etc.
        """
        self.brand_config = brand_config or {}
        logger.info("ComplianceChecker initialized")
    
    def check_legal_content(self, text: str) -> Dict:
        """
        Check text for prohibited marketing terms.
        
        Args:
            text: Campaign message or other text content
            
        Returns:
            Dictionary with compliance status and violations
        """
        violations = []
        text_lower = text.lower()
        
        for word in self.PROHIBITED_WORDS:
            if word in text_lower:
                violations.append({
                    "term": word,
                    "reason": "Prohibited marketing claim",
                    "severity": "high"
                })
        
        compliant = len(violations) == 0
        
        result = {
            "compliant": compliant,
            "violations": violations,
            "text_checked": text
        }
        
        if not compliant:
            logger.warning(f"⚠️  Legal compliance issues found: {len(violations)} violations")
            for v in violations:
                logger.warning(f"   - '{v['term']}': {v['reason']}")
        else:
            logger.info("✓ Legal content check passed")
        
        return result
    
    def check_logo_presence(self, image_path: Path, logo_path: Path = None) -> Dict:
        """
        Verify logo appears in final image using simple template matching.
        
        Args:
            image_path: Path to generated image
            logo_path: Path to logo template
            
        Returns:
            Dictionary with detection status and confidence
        """
        if logo_path is None:
            logo_path = self.brand_config.get('logo_path')
        
        if not logo_path or not Path(logo_path).exists():
            return {
                "detected": None,
                "confidence": 0.0,
                "message": "Logo template not available for checking"
            }
        
        try:
            # Load images
            image = Image.open(image_path).convert('RGB')
            logo = Image.open(logo_path).convert('RGB')
            
            # Simple check: logo should be much smaller than image
            if logo.width >= image.width * 0.3:
                logger.warning("Logo template is too large for reliable detection")
                return {
                    "detected": None,
                    "confidence": 0.0,
                    "message": "Logo template too large for detection"
                }
            
            # Convert to numpy for simple correlation check
            img_array = np.array(image)
            logo_array = np.array(logo)
            
            # Very basic presence check - just verify logo colors exist in image
            # (Real implementation would use template matching or feature detection)
            logo_colors = logo_array.reshape(-1, 3)
            unique_logo_colors = np.unique(logo_colors, axis=0)
            
            # Check if distinctive logo colors appear in the image
            # This is a simplified heuristic
            color_matches = 0
            for color in unique_logo_colors[:10]:  # Check top 10 colors
                # Check if similar colors exist in image
                img_colors = img_array.reshape(-1, 3)
                distances = np.sqrt(np.sum((img_colors - color) ** 2, axis=1))
                if np.min(distances) < 50:  # Color similarity threshold
                    color_matches += 1
            
            confidence = color_matches / min(10, len(unique_logo_colors))
            detected = confidence > 0.5
            
            result = {
                "detected": detected,
                "confidence": float(confidence),
                "message": "Logo likely present" if detected else "Logo may not be present"
            }
            
            if detected:
                logger.info(f"✓ Logo detection: {confidence:.2%} confidence")
            else:
                logger.warning(f"⚠️  Logo detection: {confidence:.2%} confidence (low)")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to check logo presence: {e}")
            return {
                "detected": None,
                "confidence": 0.0,
                "message": f"Error during detection: {str(e)}"
            }
    
    def validate_brand_colors(self, image_path: Path, brand_colors: List[str] = None) -> Dict:
        """
        Check if brand colors are present in the image.
        
        Args:
            image_path: Path to generated image
            brand_colors: List of hex color codes
            
        Returns:
            Dictionary with color presence validation
        """
        if brand_colors is None:
            brand_colors = [
                self.brand_config.get('primary_color'),
                self.brand_config.get('secondary_color')
            ]
            brand_colors = [c for c in brand_colors if c]
        
        if not brand_colors:
            return {
                "compliant": None,
                "message": "No brand colors configured for checking"
            }
        
        try:
            image = Image.open(image_path).convert('RGB')
            img_array = np.array(image)
            
            colors_found = []
            for hex_color in brand_colors:
                # Convert hex to RGB
                hex_color = hex_color.lstrip('#')
                target_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                
                # Check if similar color exists in image
                img_colors = img_array.reshape(-1, 3)
                distances = np.sqrt(np.sum((img_colors - np.array(target_rgb)) ** 2, axis=1))
                
                if np.min(distances) < 80:  # Generous threshold for color presence
                    colors_found.append(hex_color)
            
            compliant = len(colors_found) > 0
            
            result = {
                "compliant": compliant,
                "brand_colors_checked": brand_colors,
                "colors_detected": colors_found,
                "detection_rate": len(colors_found) / len(brand_colors)
            }
            
            if compliant:
                logger.info(f"✓ Brand colors detected: {len(colors_found)}/{len(brand_colors)}")
            else:
                logger.warning("⚠️  No brand colors detected in image")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to validate brand colors: {e}")
            return {
                "compliant": None,
                "message": f"Error during validation: {str(e)}"
            }
    
    def check_text_contrast(self, text_color: Tuple[int, int, int], 
                           bg_color: Tuple[int, int, int]) -> Dict:
        """
        Ensure text meets WCAG accessibility standards (4.5:1 ratio for AA).
        
        Args:
            text_color: RGB tuple for text
            bg_color: RGB tuple for background
            
        Returns:
            Dictionary with contrast ratio and compliance status
        """
        def luminance(color):
            """Calculate relative luminance."""
            rgb = [c / 255.0 for c in color]
            rgb = [
                c / 12.92 if c <= 0.03928 
                else ((c + 0.055) / 1.055) ** 2.4 
                for c in rgb
            ]
            return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
        
        l1 = luminance(text_color)
        l2 = luminance(bg_color)
        
        if l1 > l2:
            ratio = (l1 + 0.05) / (l2 + 0.05)
        else:
            ratio = (l2 + 0.05) / (l1 + 0.05)
        
        result = {
            "ratio": round(ratio, 2),
            "passes_aa": ratio >= 4.5,  # WCAG AA
            "passes_aaa": ratio >= 7.0,  # WCAG AAA
            "recommendation": "Compliant" if ratio >= 4.5 else "Increase contrast"
        }
        
        if result["passes_aa"]:
            logger.info(f"✓ Text contrast: {ratio:.2f}:1 (WCAG AA compliant)")
        else:
            logger.warning(f"⚠️  Text contrast: {ratio:.2f}:1 (Below WCAG AA)")
        
        return result
    
    def run_full_compliance_check(self, image_path: Path, campaign_message: str) -> Dict:
        """
        Run all compliance checks on a generated asset.
        
        Args:
            image_path: Path to generated image
            campaign_message: Campaign text to check
            
        Returns:
            Comprehensive compliance report
        """
        logger.info(f"Running compliance checks on {image_path.name}...")
        
        report = {
            "image": str(image_path),
            "timestamp": Path(image_path).stat().st_mtime,
            "checks": {}
        }
        
        # Legal content check
        report["checks"]["legal_content"] = self.check_legal_content(campaign_message)
        
        # Logo presence check
        report["checks"]["logo_presence"] = self.check_logo_presence(image_path)
        
        # Brand color validation
        report["checks"]["brand_colors"] = self.validate_brand_colors(image_path)
        
        # Overall compliance
        legal_ok = report["checks"]["legal_content"]["compliant"]
        logo_ok = report["checks"]["logo_presence"].get("detected", True)  # None = skip
        colors_ok = report["checks"]["brand_colors"].get("compliant", True)  # None = skip
        
        # Only fail if we have definitive failures
        report["overall_compliant"] = legal_ok and (logo_ok is not False) and (colors_ok is not False)
        
        if report["overall_compliant"]:
            logger.info(f"✅ Overall compliance: PASSED")
        else:
            logger.warning(f"⚠️  Overall compliance: ISSUES DETECTED")
        
        return report