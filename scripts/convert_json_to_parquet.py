"""
Convert JSON dataset files to Parquet format.
This script reads JSON array files from the datasets folder and converts them
to Parquet format, saving them to the datasets_dist folder.
"""

import json
import pandas as pd
from pathlib import Path
import argparse
import sys


def convert_json_to_parquet(json_file: Path, output_dir: Path) -> None:
    """
    Convert a JSON file to Parquet format.
    
    Args:
        json_file: Path to the input JSON file
        output_dir: Path to the output directory
    """
    print(f"Processing: {json_file.name}")
    
    try:
        # Read JSON file
        print(f"  Reading JSON file...")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"  Loaded {len(data)} records")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        print(f"  DataFrame shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename (replace .json with .parquet)
        output_file = output_dir / json_file.name.replace('.json', '.parquet')
        
        # Save as Parquet
        print(f"  Saving to: {output_file}")
        df.to_parquet(output_file, engine='pyarrow', compression='snappy', index=False)
        
        # Verify the file was created
        if output_file.exists():
            file_size = output_file.stat().st_size / 1024  # Size in KB
            print(f"  ✓ Successfully created: {output_file.name} ({file_size:.2f} KB)")
        else:
            print(f"  ✗ Error: File was not created")
            
    except json.JSONDecodeError as e:
        print(f"  ✗ Error: Invalid JSON file - {e}")
    except Exception as e:
        print(f"  ✗ Error: {e}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Convert JSON dataset files to Parquet format'
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Specific JSON file(s) to convert. If not provided, converts all compare_training_dataset_*.json files'
    )
    parser.add_argument(
        '--input-dir',
        type=str,
        default='datasets',
        help='Input directory containing JSON files (default: datasets)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='datasets_dist',
        help='Output directory for Parquet files (default: datasets_dist)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Convert all JSON files in the input directory'
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)
    
    print("=" * 60)
    print("JSON to Parquet Converter")
    print("=" * 60)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Determine which files to convert
    json_files = []
    
    if args.files:
        # Convert specific files
        for file_name in args.files:
            file_path = input_dir / file_name
            if file_path.exists():
                json_files.append(file_path)
            else:
                print(f"Warning: File not found: {file_path}")
    elif args.all:
        # Convert all JSON files
        json_files = list(input_dir.glob('*.json'))
    else:
        # Default: Convert all compare_training_dataset_*.json files
        json_files = list(input_dir.glob('compare_training_dataset_*.json'))
    
    if not json_files:
        print("No JSON files found to convert.")
        print()
        print("Usage examples:")
        print("  # Convert specific file:")
        print("  python convert_json_to_parquet.py compare_training_dataset_20260104_150216.json")
        print()
        print("  # Convert all compare_training_dataset_*.json files (default):")
        print("  python convert_json_to_parquet.py")
        print()
        print("  # Convert all JSON files:")
        print("  python convert_json_to_parquet.py --all")
        sys.exit(0)
    
    print(f"Found {len(json_files)} file(s) to convert:")
    for f in json_files:
        print(f"  - {f.name}")
    print()
    
    # Convert each file
    success_count = 0
    for json_file in json_files:
        try:
            convert_json_to_parquet(json_file, output_dir)
            success_count += 1
            print()
        except Exception as e:
            print(f"  Failed to convert {json_file.name}: {e}")
            print()
    
    print("=" * 60)
    print(f"Conversion complete: {success_count}/{len(json_files)} files successful")
    print("=" * 60)


if __name__ == "__main__":
    main()
