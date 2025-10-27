#!/usr/bin/env python3
"""
Creative Automation Pipeline - Main Orchestration Script

This script orchestrates the entire creative automation pipeline with:
- Progress tracking (tqdm)
- Parallel image generation
- Brand compliance checks
- Legal content validation
- Enhanced logging and reporting

Usage:
    python pipeline.py --brief campaign_briefs/spring_fitness_2025.json
    python pipeline.py --brief campaign_briefs/spring_fitness_2025.json --verbose
    python pipeline.py --brief campaign_briefs/spring_fitness_2025.json --skip-compliance
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Import our modules
from src.utils import (
    setup_logging, load_campaign_brief, create_output_structure, 
    generate_execution_report, calculate_estimated_cost
)
from src.asset_manager import AssetManager
from src.prompt_engineer import PromptEngineer
from src.image_generator import ImageGenerator
from src.creative_composer import CreativeComposer
from src.compliance_checker import ComplianceChecker


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Creative Automation Pipeline - Generate social media creative assets using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --brief campaign_briefs/spring_fitness_2025.json
  python pipeline.py --brief campaign_briefs/my_campaign.json --verbose
  python pipeline.py --brief campaign_briefs/quick_test.json --skip-compliance
  
For more information, see README.md
        """
    )
    parser.add_argument(
        "--brief",
        type=str,
        required=True,
        help="Path to campaign brief JSON file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--skip-generation",
        action="store_true",
        help="Skip image generation (useful for testing composition only)"
    )
    parser.add_argument(
        "--skip-compliance",
        action="store_true",
        help="Skip compliance checks"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Generate images in parallel (faster, experimental)"
    )
    return parser.parse_args()


def generate_single_image(product, campaign_brief, prompt_engineer, image_generator, asset_manager):
    """
    Generate a single product image.
    
    Args:
        product: Product dictionary
        campaign_brief: Full campaign brief
        prompt_engineer: PromptEngineer instance
        image_generator: ImageGenerator instance
        asset_manager: AssetManager instance
        
    Returns:
        Tuple of (product_id, saved_path) or (product_id, None) on failure
    """
    product_id = product.get("id")
    product_name = product.get("name", product_id)
    
    try:
        # Generate optimized prompt using GPT-4
        prompt = prompt_engineer.create_image_prompt(campaign_brief, product)
        
        # Generate image using Flux
        image_url = image_generator.generate_with_flux(prompt, image_size="16x9")
        
        # Save generated image
        saved_path = asset_manager.save_generated_image(image_url, product_id)
        
        return (product_id, saved_path)
        
    except Exception as e:
        logging.error(f"Failed to generate {product_name}: {e}")
        return (product_id, None)


def main():
    """Main pipeline orchestration."""
    # Parse arguments
    args = parse_arguments()
    
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    # Print banner
    print("\n" + "="*70)
    print("🚀 CREATIVE AUTOMATION PIPELINE")
    print("="*70 + "\n")
    
    logger.info(f"📄 Loading campaign brief: {args.brief}")
    
    start_time = time.time()
    
    # Tracking metrics
    gpt4_calls = 0
    flux_calls = 0
    compliance_reports = []
    
    try:
        # =================================================================
        # STEP 1: Load Campaign Brief
        # =================================================================
        brief_path = Path(args.brief)
        if not brief_path.exists():
            raise FileNotFoundError(f"Campaign brief not found: {args.brief}")
        
        campaign_brief = load_campaign_brief(brief_path)
        campaign_id = campaign_brief.get("campaign_id", "campaign")
        campaign_name = campaign_brief.get("campaign_name", campaign_id)
        products = campaign_brief.get("products", [])
        campaign_message = campaign_brief.get("campaign_message", "")
        
        logger.info(f"✓ Campaign: {campaign_name}")
        logger.info(f"✓ Products: {len(products)}")
        logger.info(f"✓ Message: {campaign_message}")
        
        if len(products) == 0:
            raise ValueError("No products found in campaign brief")
        
        # =================================================================
        # STEP 2: Initialize Components
        # =================================================================
        logger.info("\n🔧 Initializing components...")
        
        asset_manager = AssetManager()
        prompt_engineer = PromptEngineer()
        image_generator = ImageGenerator()
        
        brand_config = campaign_brief.get("brand_config", {})
        composer = CreativeComposer(brand_config)
        
        # Initialize compliance checker
        if not args.skip_compliance:
            compliance_checker = ComplianceChecker(brand_config)
            
            # Check campaign message for legal compliance
            logger.info("\n⚖️  Checking legal compliance...")
            legal_check = compliance_checker.check_legal_content(campaign_message)
            if not legal_check["compliant"]:
                logger.warning("⚠️  Legal compliance issues detected - review recommended")
        
        logger.info("✓ All components initialized")
        
        # =================================================================
        # STEP 3: Check Existing Assets
        # =================================================================
        logger.info("\n📦 Checking existing assets...")
        
        existing_assets, missing_products = asset_manager.check_existing_assets(products)
        
        logger.info(f"✓ Found {len(existing_assets)} existing assets")
        logger.info(f"✓ Need to generate {len(missing_products)} new assets")
        
        # =================================================================
        # STEP 4: Generate Missing Assets
        # =================================================================
        generated_count = 0
        
        if missing_products and not args.skip_generation:
            logger.info("\n🎨 Generating missing product images...")
            
            if args.parallel and len(missing_products) > 1:
                # Parallel generation (experimental)
                logger.info("   Using parallel processing...")
                
                with ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_product = {
                        executor.submit(
                            generate_single_image,
                            product,
                            campaign_brief,
                            prompt_engineer,
                            image_generator,
                            asset_manager
                        ): product
                        for product in missing_products
                    }
                    
                    with tqdm(total=len(missing_products), desc="🎨 Generating images") as pbar:
                        for future in as_completed(future_to_product):
                            product = future_to_product[future]
                            product_id, saved_path = future.result()
                            
                            if saved_path:
                                existing_assets[product_id] = saved_path
                                generated_count += 1
                                gpt4_calls += 1
                                flux_calls += 1
                            
                            pbar.update(1)
            else:
                # Sequential generation with progress bar
                for product in tqdm(missing_products, desc="🎨 Generating images"):
                    product_id, saved_path = generate_single_image(
                        product,
                        campaign_brief,
                        prompt_engineer,
                        image_generator,
                        asset_manager
                    )
                    
                    if saved_path:
                        existing_assets[product_id] = saved_path
                        generated_count += 1
                        gpt4_calls += 1
                        flux_calls += 1
            
            logger.info(f"\n✓ Generated {generated_count} new images")
        
        elif args.skip_generation:
            logger.info("⚠️  Skipping image generation (--skip-generation flag)")
        
        # =================================================================
        # STEP 5: Create Variations for All Products
        # =================================================================
        logger.info("\n🖼️  Creating aspect ratio variations...")
        
        output_base = create_output_structure(campaign_id, products)
        aspect_ratios = campaign_brief.get("aspect_ratios", ["1x1", "9x16", "16x9"])
        
        total_variations = 0
        
        for product_id, hero_image_path in tqdm(
            existing_assets.items(), 
            desc="🖼️  Creating variations"
        ):
            product_name = next(
                (p.get("name", product_id) for p in products if p.get("id") == product_id),
                product_id
            )
            
            try:
                variations = composer.create_variations(
                    hero_image_path,
                    campaign_message,
                    product_id,
                    output_base,
                    ratios=aspect_ratios
                )
                
                total_variations += len(variations)
                
                # Run compliance checks on generated variations
                if not args.skip_compliance:
                    for var_path in variations:
                        compliance_report = compliance_checker.run_full_compliance_check(
                            var_path,
                            campaign_message
                        )
                        compliance_reports.append(compliance_report)
                
            except Exception as e:
                logger.error(f"✗ Failed to create variations for {product_name}: {e}")
                continue
        
        # =================================================================
        # STEP 6: Summary & Reporting
        # =================================================================
        elapsed_time = time.time() - start_time
        estimated_cost = calculate_estimated_cost(gpt4_calls, flux_calls)
        
        summary = {
            "Campaign ID": campaign_id,
            "Campaign": campaign_name,
            "Campaign Message": campaign_message,
            "Products Processed": len(products),
            "Existing Assets": len(existing_assets) - generated_count,
            "Generated Assets": generated_count,
            "Total Variations Created": total_variations,
            "GPT-4 Calls": gpt4_calls,
            "Flux Calls": flux_calls,
            "Estimated Cost": f"${estimated_cost}",
            "Total Time": f"{elapsed_time:.2f} seconds",
            "Output Location": str(output_base)
        }
        
        # Generate detailed JSON report
        logger.info("\n📊 Generating execution report...")
        report_path = generate_execution_report(summary, output_base, compliance_reports)
        logger.info(f"✓ Report saved: {report_path}")
        
        # Print summary
        print("\n" + "="*70)
        print("📊 PIPELINE SUMMARY")
        print("="*70)
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        if not args.skip_compliance and compliance_reports:
            compliant_count = sum(1 for r in compliance_reports if r.get("overall_compliant", False))
            print(f"\n  Compliance Checks: {compliant_count}/{len(compliance_reports)} passed")
        
        print("="*70 + "\n")
        
        # Show output structure
        print("📁 Output Structure:")
        print(f"  {output_base}/")
        for product_id in existing_assets.keys():
            product_folder = output_base / product_id
            if product_folder.exists():
                print(f"    ├── {product_id}/")
                for ratio in aspect_ratios:
                    ratio_file = product_folder / f"{ratio}.png"
                    if ratio_file.exists():
                        print(f"    │   ├── {ratio}.png")
        
        print(f"\n✅ Pipeline completed successfully!")
        print(f"🎉 Your campaign assets are ready in: {output_base}")
        print(f"📊 Detailed report: {report_path}\n")
        
        logger.info("="*70)
        logger.info("Pipeline execution completed")
        logger.info("="*70)
        
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"\n\n❌ Pipeline failed: {str(e)}")
        if args.verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()