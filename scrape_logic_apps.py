"""
Main script to run the full scraping and dataset creation pipeline.
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from scrapers import DatasetBuilder


def main():
    parser = argparse.ArgumentParser(
        description='Scrape Azure Logic App expressions from GitHub for fine-tuning'
    )
    parser.add_argument(
        '--max-files',
        type=int,
        default=1500,
        help='Maximum number of workflow files to scrape (default: 100)'
    )
    parser.add_argument(
        '--min-quality',
        type=float,
        default=0.0,
        help='Minimum quality score for training samples (default: 0.5)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='datasets',
        help='Output directory for datasets (default: datasets)'
    )
    parser.add_argument(
        '--no-deduplicate',
        action='store_true',
        help='Do not remove duplicate expressions'
    )
    parser.add_argument(
        '--patterns',
        nargs='+',
        help='Specific expression patterns to search for (e.g., concat variables triggerBody)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Azure Logic App Expression Dataset Builder")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Max files: {args.max_files}")
    print(f"  Min quality: {args.min_quality}")
    print(f"  Output directory: {args.output_dir}")
    print(f"  Deduplicate: {not args.no_deduplicate}")
    if args.patterns:
        print(f"  Search patterns: {', '.join(args.patterns)}")
    
    # Initialize builder
    builder = DatasetBuilder(output_dir=args.output_dir)
    builder.initialize_scraper()
    
    # Check rate limits
    rate_info = builder.scraper.get_rate_limit_info()
    print(f"\nGitHub API Rate Limits:")
    print(f"  Search: {rate_info.get('search_remaining', 'N/A')}/{rate_info.get('search_limit', 'N/A')}")
    print(f"  Core: {rate_info.get('core_remaining', 'N/A')}/{rate_info.get('core_limit', 'N/A')}")
    
    if rate_info.get('search_remaining', 0) < 10:
        print("\n⚠️  Warning: Low search API rate limit. Consider using a GitHub token.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Step 1: Scrape workflows
    print("\n" + "=" * 70)
    print("STEP 1: Scraping Logic App Workflows from GitHub")
    print("=" * 70)
    
    num_files = builder.scrape_workflows(
        max_files=args.max_files,
        search_patterns=args.patterns
    )
    
    if num_files == 0:
        print("\n❌ No files found. Try adjusting your search parameters.")
        return
    
    print(f"\n✅ Found {num_files} workflow files")
    
    # Step 2: Download and parse
    print("\n" + "=" * 70)
    print("STEP 2: Downloading and Parsing Workflows")
    print("=" * 70)
    
    num_workflows = builder.download_and_parse_workflows()
    
    if num_workflows == 0:
        print("\n❌ No valid workflows found. Files may not be Logic App workflows.")
        return
    
    print(f"\n✅ Successfully parsed {num_workflows} workflows")
    
    # Step 3: Create training dataset
    print("\n" + "=" * 70)
    print("STEP 3: Creating Training Dataset")
    print("=" * 70)
    
    num_samples = builder.create_training_dataset(
        min_quality_score=args.min_quality,
        deduplicate=not args.no_deduplicate
    )
    
    if num_samples == 0:
        print("\n❌ No training samples created. Try lowering min_quality.")
        return
    
    print(f"\n✅ Created {num_samples} training samples")
    
    # Step 4: Generate statistics
    print("\n" + "=" * 70)
    print("STEP 4: Generating Statistics Report")
    print("=" * 70)
    
    report = builder.generate_statistics_report()
    
    # Summary
    print("\n" + "=" * 70)
    print("✨ DATASET CREATION COMPLETE!")
    print("=" * 70)
    print(f"\nDataset Summary:")
    print(f"  📊 Total training samples: {num_samples}")
    print(f"  🔄 Unique expressions: {report.get('unique_expressions', 'N/A')}")
    print(f"  📁 Source workflows: {num_workflows}")
    print(f"  ⭐ Avg quality score: {report.get('avg_quality_score', 0):.2f}")
    print(f"  🔧 Avg functions per expression: {report.get('avg_function_count', 0):.2f}")
    
    print(f"\n📂 Output files saved to: {args.output_dir}/")
    print(f"  - training_dataset_*.jsonl (for fine-tuning)")
    print(f"  - training_dataset_*.json (full data)")
    print(f"  - training_dataset_*.csv (for analysis)")
    print(f"  - processed_workflows.json (workflow data)")
    print(f"  - dataset_statistics.json (statistics)")
    
    print("\n🚀 Next steps:")
    print("  1. Review the CSV file to inspect the dataset")
    print("  2. Use the JSONL file for fine-tuning your model")
    print("  3. Adjust parameters and run again to expand the dataset")


if __name__ == '__main__':
    main()
