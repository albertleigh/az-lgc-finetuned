"""
Script to upload datasets to Hugging Face Hub.
This script uploads parquet files to a Hugging Face dataset repository.
"""

import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_file
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def upload_datasets_to_hf(
    repo_id: str,
    token: str = None,
    datasets_dir: str = "datasets_dist",
    training_file: str = "training_dataset_v1.parquet",
    categorization_file: str = "training_dataset_categorization_v1.parquet",
    repo_type: str = "dataset",
    private: bool = False
):
    """
    Upload datasets to Hugging Face Hub.
    
    Args:
        repo_id: The repository ID on Hugging Face (e.g., 'username/dataset-name')
        token: Hugging Face API token. If None, will use HF_TOKEN environment variable
        datasets_dir: Directory containing the parquet files
        training_file: Name of the training dataset file
        categorization_file: Name of the categorization dataset file
        repo_type: Type of repository ('dataset' by default)
        private: Whether to create a private repository
    """

    # Initialize Hugging Face API
    api = HfApi()
    
    # Use token from environment if not provided
    if token is None:
        token = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError(
                "No Hugging Face token provided. Either pass token parameter, "
                "set HF_TOKEN environment variable, or add HF_TOKEN to .env file."
            )
    
    # Get workspace root (parent of scripts directory)
    workspace_root = Path(__file__).parent.parent
    datasets_path = workspace_root / datasets_dir
    
    # Verify files exist
    training_path = datasets_path / training_file
    categorization_path = datasets_path / categorization_file
    
    if not training_path.exists():
        raise FileNotFoundError(f"Training dataset not found: {training_path}")
    if not categorization_path.exists():
        raise FileNotFoundError(f"Categorization dataset not found: {categorization_path}")
    
    print(f"Found datasets:")
    print(f"  - Training: {training_path} ({training_path.stat().st_size / 1024 / 1024:.2f} MB)")
    print(f"  - Categorization: {categorization_path} ({categorization_path.stat().st_size / 1024 / 1024:.2f} MB)")
    
    # Create repository if it doesn't exist
    try:
        print(f"\nCreating/accessing repository: {repo_id}")
        create_repo(
            repo_id=repo_id,
            token=token,
            repo_type=repo_type,
            private=private,
            exist_ok=True
        )
        print(f"✓ Repository ready: https://huggingface.co/datasets/{repo_id}")
    except Exception as e:
        print(f"Error creating repository: {e}")
        raise
    
    # Upload training dataset
    print(f"\nUploading training dataset...")
    try:
        upload_file(
            path_or_fileobj=str(training_path),
            path_in_repo=f"train/{training_file}",
            repo_id=repo_id,
            repo_type=repo_type,
            token=token,
        )
        print(f"✓ Uploaded: train/{training_file}")
    except Exception as e:
        print(f"Error uploading training dataset: {e}")
        raise
    
    # Upload categorization dataset
    print(f"\nUploading categorization dataset...")
    try:
        upload_file(
            path_or_fileobj=str(categorization_path),
            path_in_repo=f"categorization/{categorization_file}",
            repo_id=repo_id,
            repo_type=repo_type,
            token=token,
        )
        print(f"✓ Uploaded: categorization/{categorization_file}")
    except Exception as e:
        print(f"Error uploading categorization dataset: {e}")
        raise
    
    # Create a README.md if it doesn't exist
    print(f"\nCreating README.md...")
    readme_content = f"""---
license: mit
task_categories:
- text-generation
- text-classification
language:
- en
tags:
- azure
- logic-apps
- workflow
- expressions
size_categories:
- n<1K
---

# Azure Logic Apps Expression Dataset

This dataset contains Azure Logic Apps workflow expressions and metadata for training models.

## Dataset Structure

The dataset is organized into two main splits:

### Training Dataset (`train/`)
- File: `{training_file}`
- Purpose: Primary training data for Azure Logic Apps expression generation
- Format: Parquet

### Categorization Dataset (`categorization/`)
- File: `{categorization_file}`
- Purpose: Training data for categorizing and understanding Azure Logic Apps expressions
- Format: Parquet

## Usage

```python
from datasets import load_dataset

# Load training dataset
train_ds = load_dataset("{repo_id}", data_files="train/{training_file}")

# Load categorization dataset
cat_ds = load_dataset("{repo_id}", data_files="categorization/{categorization_file}")
```

## License

This dataset is released under the MIT License.

## Citation

If you use this dataset, please cite it appropriately.
"""
    
    try:
        upload_file(
            path_or_fileobj=readme_content.encode(),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type=repo_type,
            token=token,
        )
        print(f"✓ Created README.md")
    except Exception as e:
        print(f"Note: Could not create README.md: {e}")
    
    print(f"\n✅ All datasets uploaded successfully!")
    print(f"🔗 View your dataset at: https://huggingface.co/datasets/{repo_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Upload datasets to Hugging Face Hub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload with token from .env file (HF_TOKEN=hf_xxxxx)
  python upload_to_huggingface.py username/az-logic-apps-dataset

  # Upload with token from environment variable HF_TOKEN
  python upload_to_huggingface.py username/az-logic-apps-dataset

  # Upload with explicit token
  python upload_to_huggingface.py username/az-logic-apps-dataset --token hf_xxxxx

  # Upload as private dataset
  python upload_to_huggingface.py username/az-logic-apps-dataset --private

  # Custom file names
  python upload_to_huggingface.py username/dataset --training-file train.parquet --categorization-file cat.parquet
        """
    )
    
    parser.add_argument(
        "repo_id",
        type=str,
        help="Repository ID on Hugging Face (e.g., 'username/dataset-name')"
    )
    
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Hugging Face API token (defaults to HF_TOKEN from .env file or environment variable)"
    )
    
    parser.add_argument(
        "--datasets-dir",
        type=str,
        default="datasets_dist",
        help="Directory containing the parquet files (default: datasets_dist)"
    )
    
    parser.add_argument(
        "--training-file",
        type=str,
        default="training_dataset_v1.parquet",
        help="Name of the training dataset file"
    )
    
    parser.add_argument(
        "--categorization-file",
        type=str,
        default="training_dataset_categorization_v1.parquet",
        help="Name of the categorization dataset file"
    )
    
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create a private repository"
    )
    
    args = parser.parse_args()
    
    try:
        upload_datasets_to_hf(
            repo_id=args.repo_id,
            token=args.token,
            datasets_dir=args.datasets_dir,
            training_file=args.training_file,
            categorization_file=args.categorization_file,
            private=args.private
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

# python scripts/upload_to_huggingface.py albertleigh/az-logic-apps-dataset
if __name__ == "__main__":
    exit(main())
