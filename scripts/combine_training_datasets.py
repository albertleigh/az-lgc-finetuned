"""
Combine multiple training dataset JSON files into a single file.
This script reads all training_dataset_*.json files from the datasets/updated folder
and combines them into one comprehensive dataset.
"""

import json
from pathlib import Path
from datetime import datetime
import argparse
import sys


def load_json_file(file_path: Path) -> list:
    """
    Load a JSON array from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of records from the JSON file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print(f"  Warning: {file_path.name} is not a JSON array, skipping")
            return []
        
        return data
    except json.JSONDecodeError as e:
        print(f"  Error: Invalid JSON in {file_path.name} - {e}")
        return []
    except Exception as e:
        print(f"  Error reading {file_path.name}: {e}")
        return []


def combine_datasets(input_dir: Path, output_dir: Path) -> None:
    """
    Combine all training dataset JSON files into one.
    
    Args:
        input_dir: Directory containing the JSON files to combine
        output_dir: Directory where the combined file will be saved
    """
    print("=" * 60)
    print("Combining Training Datasets")
    print("=" * 60)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Find all training_dataset_*.json files
    json_files = sorted(input_dir.glob('training_dataset_*.json'))
    
    if not json_files:
        print(f"No training_dataset_*.json files found in {input_dir}")
        sys.exit(1)
    
    print(f"Found {len(json_files)} file(s) to combine:")
    for f in json_files:
        print(f"  - {f.name}")
    print()
    
    # Combine all datasets
    combined_data = []
    file_stats = []
    
    for json_file in json_files:
        print(f"Loading: {json_file.name}")
        data = load_json_file(json_file)
        
        if data:
            record_count = len(data)
            print(f"  Loaded {record_count} records")
            combined_data.extend(data)
            file_stats.append({
                'filename': json_file.name,
                'records': record_count
            })
        else:
            print(f"  No records loaded")
        print()
    
    total_records = len(combined_data)
    print(f"Total combined records: {total_records}")
    print()
    
    if total_records == 0:
        print("No records to save. Exiting.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"training_dataset_{timestamp}_combined.json"
    
    # Save combined dataset
    print(f"Saving combined dataset to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    
    # Verify file was created
    if output_file.exists():
        file_size = output_file.stat().st_size / (1024 * 1024)  # Size in MB
        print(f"✓ Successfully created: {output_file.name}")
        print(f"  File size: {file_size:.2f} MB")
    else:
        print("✗ Error: File was not created")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Combination Summary")
    print("=" * 60)
    print(f"Files combined: {len(file_stats)}")
    print()
    
    for stat in file_stats:
        percentage = (stat['records'] / total_records) * 100
        print(f"  {stat['filename']}: {stat['records']:,} records ({percentage:.1f}%)")
    
    print()
    print(f"Total records in combined file: {total_records:,}")
    print(f"Output file: {output_file}")
    print("=" * 60)
    
    # Print sample record
    if combined_data:
        print()
        print("Sample record from combined dataset:")
        print(json.dumps(combined_data[0], indent=2))


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Combine multiple training dataset JSON files into one'
    )
    parser.add_argument(
        '--input-dir',
        type=str,
        default='datasets/updated',
        help='Input directory containing JSON files (default: datasets/updated)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='datasets',
        help='Output directory for combined file (default: datasets)'
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)
    
    combine_datasets(input_dir, output_dir)


if __name__ == "__main__":
    main()
