"""
Utility functions for the Creative Automation Pipeline.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_campaign_brief(brief_path: Path) -> Dict[str, Any]:
    """
    Load campaign brief from JSON file.
    
    Args:
        brief_path: Path to JSON campaign brief
        
    Returns:
        Campaign brief dictionary
    """
    with open(brief_path, 'r') as f:
        return json.load(f)


def create_output_structure(campaign_id: str, products: list) -> Path:
    """
    Create organized output folder structure.
    
    Args:
        campaign_id: Campaign identifier
        products: List of products
        
    Returns:
        Path to campaign output folder
    """
    base_path = Path("outputs") / campaign_id
    base_path.mkdir(parents=True, exist_ok=True)
    
    for product in products:
        product_path = base_path / product["id"]
        product_path.mkdir(exist_ok=True)
    
    return base_path


def log_summary(summary: Dict[str, Any]) -> None:
    """
    Log pipeline execution summary.
    
    Args:
        summary: Dictionary with execution metrics
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("PIPELINE EXECUTION SUMMARY")
    logger.info("=" * 60)
    for key, value in summary.items():
        logger.info(f"{key}: {value}")
    logger.info("=" * 60)


def list_output_files(output_path: Path) -> List[Dict[str, str]]:
    """
    List all generated output files.
    
    Args:
        output_path: Path to output directory
        
    Returns:
        List of file information dictionaries
    """
    files = []
    
    for file_path in output_path.rglob("*.png"):
        rel_path = file_path.relative_to(output_path)
        files.append({
            "path": str(rel_path),
            "size_kb": round(file_path.stat().st_size / 1024, 2),
            "product": rel_path.parts[0] if len(rel_path.parts) > 1 else "unknown",
            "variant": file_path.stem
        })
    
    return files


def generate_execution_report(summary: Dict[str, Any], 
                              output_path: Path,
                              compliance_reports: List[Dict] = None) -> Path:
    """
    Generate detailed JSON report of pipeline execution.
    
    Args:
        summary: Summary dictionary with metrics
        output_path: Path to output directory
        compliance_reports: Optional list of compliance check results
        
    Returns:
        Path to generated report file
    """
    report = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "pipeline_version": "1.0.0",
            "execution_mode": "standard"
        },
        "campaign": {
            "id": summary.get("Campaign ID", "unknown"),
            "name": summary.get("Campaign", "unknown"),
            "message": summary.get("Campaign Message", "")
        },
        "metrics": {
            "products_processed": summary.get("Products Processed", 0),
            "assets_existing": summary.get("Existing Assets", 0),
            "assets_generated": summary.get("Generated Assets", 0),
            "variations_created": summary.get("Total Variations Created", 0),
            "execution_time_seconds": float(summary.get("Total Time", "0").replace(" seconds", ""))
        },
        "api_usage": {
            "openai_calls": summary.get("GPT-4 Calls", 0),
            "flux_calls": summary.get("Flux Calls", 0),
            "estimated_cost_usd": summary.get("Estimated Cost", 0.0)
        },
        "outputs": {
            "location": str(output_path),
            "files": list_output_files(output_path)
        }
    }
    
    # Add compliance reports if available
    if compliance_reports:
        report["compliance"] = {
            "checks_performed": len(compliance_reports),
            "reports": compliance_reports
        }
    
    # Save report
    report_path = output_path / "execution_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report_path


def calculate_estimated_cost(gpt4_calls: int, flux_calls: int) -> float:
    """
    Calculate estimated API costs.
    
    Args:
        gpt4_calls: Number of GPT-4 API calls
        flux_calls: Number of Flux generation calls
        
    Returns:
        Estimated cost in USD
    """
    # Rough estimates (actual costs may vary)
    GPT4_COST_PER_CALL = 0.01  # ~1000 tokens at $0.01/1k
    FLUX_COST_PER_IMAGE = 0.055  # fal.ai Flux Pro pricing
    
    total = (gpt4_calls * GPT4_COST_PER_CALL) + (flux_calls * FLUX_COST_PER_IMAGE)
    return round(total, 2)