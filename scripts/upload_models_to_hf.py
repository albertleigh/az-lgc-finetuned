#!/usr/bin/env python
"""
Script to upload fine-tuned models to Hugging Face Hub.
This script uploads GPT and BERT models to Hugging Face model repositories.
"""

import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def upload_model_to_hf(
    model_path: str,
    repo_id: str,
    token: str = None,
    private: bool = False,
    model_type: str = None
):
    """
    Upload a model to Hugging Face Hub.
    
    Args:
        model_path: Path to the model directory
        repo_id: The repository ID on Hugging Face (e.g., 'username/model-name')
        token: Hugging Face API token. If None, will use HF_TOKEN environment variable
        private: Whether to create a private repository
        model_type: Type of model ('gpt', 'bert', or auto-detect)
    """
    
    # Use token from environment if not provided
    if token is None:
        token = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError(
                "No Hugging Face token provided. Either pass token parameter, "
                "set HF_TOKEN environment variable, or add HF_TOKEN to .env file."
            )
    
    # Verify model path exists
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model directory not found: {model_path}")
    
    # Check for required model files
    required_files = ["config.json", "pytorch_model.bin"]
    has_safetensors = (model_path / "model.safetensors").exists()
    has_pytorch_bin = (model_path / "pytorch_model.bin").exists()
    
    if not (model_path / "config.json").exists():
        raise FileNotFoundError(f"config.json not found in {model_path}")
    
    if not (has_safetensors or has_pytorch_bin):
        raise FileNotFoundError(
            f"No model weights found in {model_path}. "
            "Expected 'model.safetensors' or 'pytorch_model.bin'"
        )
    
    # Auto-detect model type if not specified
    if model_type is None:
        model_name = model_path.name.lower()
        if "gpt" in model_name:
            model_type = "gpt"
        elif "bert" in model_name:
            model_type = "bert"
        else:
            model_type = "unknown"
    
    print(f"\n{'='*70}")
    print(f"Uploading {model_type.upper()} Model to Hugging Face")
    print(f"{'='*70}")
    print(f"Model path: {model_path}")
    print(f"Repository: {repo_id}")
    print(f"Privacy: {'Private' if private else 'Public'}")
    
    # List all files in model directory
    model_files = list(model_path.glob("*"))
    print(f"\nFiles to upload ({len(model_files)} files):")
    for file in sorted(model_files):
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  - {file.name} ({size_mb:.2f} MB)")
    
    # Initialize Hugging Face API
    api = HfApi()
    
    # Create repository if it doesn't exist
    try:
        print(f"\n{'='*70}")
        print(f"Creating/accessing repository...")
        print(f"{'='*70}")
        create_repo(
            repo_id=repo_id,
            token=token,
            repo_type="model",
            private=private,
            exist_ok=True
        )
        print(f"✓ Repository ready: https://huggingface.co/{repo_id}")
    except Exception as e:
        print(f"❌ Error creating repository: {e}")
        raise
    
    # Upload the entire model directory
    print(f"\n{'='*70}")
    print(f"Uploading model files...")
    print(f"{'='*70}")
    try:
        api.upload_folder(
            folder_path=str(model_path),
            repo_id=repo_id,
            repo_type="model",
            token=token,
        )
        print(f"✓ All files uploaded successfully!")
    except Exception as e:
        print(f"❌ Error uploading model: {e}")
        raise
    
    print(f"\n{'='*70}")
    print(f"✅ Upload Complete!")
    print(f"{'='*70}")
    print(f"🔗 View your model at: https://huggingface.co/{repo_id}")
    print(f"\n💡 You can now use your model with:")
    if model_type == "gpt":
        print(f"   from transformers import AutoModelForCausalLM, AutoTokenizer")
        print(f"   model = AutoModelForCausalLM.from_pretrained('{repo_id}')")
        print(f"   tokenizer = AutoTokenizer.from_pretrained('{repo_id}')")
    elif model_type == "bert":
        print(f"   from transformers import AutoModelForSequenceClassification, AutoTokenizer")
        print(f"   model = AutoModelForSequenceClassification.from_pretrained('{repo_id}')")
        print(f"   tokenizer = AutoTokenizer.from_pretrained('{repo_id}')")
    print()


def upload_all_models(
    models_dir: str,
    username: str,
    token: str = None,
    private: bool = False
):
    """
    Upload all models in the models directory to Hugging Face.
    
    Args:
        models_dir: Directory containing all models
        username: Your Hugging Face username
        token: Hugging Face API token
        private: Whether to create private repositories
    """
    models_dir = Path(models_dir)
    
    if not models_dir.exists():
        raise FileNotFoundError(f"Models directory not found: {models_dir}")
    
    # Find all model directories (directories containing config.json)
    model_dirs = [d for d in models_dir.iterdir() if d.is_dir() and (d / "config.json").exists()]
    
    if not model_dirs:
        print(f"⚠️  No valid models found in {models_dir}")
        print(f"   (Looking for directories with config.json)")
        return
    
    print(f"\n{'='*70}")
    print(f"Found {len(model_dirs)} model(s) to upload")
    print(f"{'='*70}")
    for model_dir in model_dirs:
        print(f"  - {model_dir.name}")
    print()
    
    # Upload each model
    for i, model_dir in enumerate(model_dirs, 1):
        repo_id = f"{username}/{model_dir.name}"
        print(f"\n[{i}/{len(model_dirs)}] Processing: {model_dir.name}")
        
        try:
            upload_model_to_hf(
                model_path=str(model_dir),
                repo_id=repo_id,
                token=token,
                private=private
            )
        except Exception as e:
            print(f"❌ Failed to upload {model_dir.name}: {e}")
            continue
    
    print(f"\n{'='*70}")
    print(f"🎉 All models processed!")
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(
        description="Upload fine-tuned models to Hugging Face Hub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload all models in models/ directory (requires HF_TOKEN in .env)
  python upload_models_to_hf.py --username albertleigh --all

  # Upload a specific model
  python upload_models_to_hf.py --model models/azLgcExpGpt_HF --repo albertleigh/azlgc-gpt

  # Upload with explicit token
  python upload_models_to_hf.py --username albertleigh --all --token hf_xxxxx

  # Upload as private models
  python upload_models_to_hf.py --username albertleigh --all --private

  # Upload specific model with custom name
  python upload_models_to_hf.py --model models/bert_classifier_azlgcexp_base --repo albertleigh/azlgc-bert-classifier
        """
    )
    
    parser.add_argument(
        "--username",
        type=str,
        help="Your Hugging Face username (required when using --all)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Upload all models from models/ directory"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Path to specific model directory to upload"
    )
    
    parser.add_argument(
        "--repo",
        type=str,
        help="Repository ID for the model (e.g., 'username/model-name'). Required when using --model"
    )
    
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Hugging Face API token (defaults to HF_TOKEN from .env file or environment variable)"
    )
    
    parser.add_argument(
        "--models-dir",
        type=str,
        default="models",
        help="Directory containing all models (default: models)"
    )
    
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create private repositories"
    )
    
    args = parser.parse_args()
    
    # Get workspace root
    workspace_root = Path(__file__).parent.parent
    
    try:
        if args.all:
            # Upload all models
            if not args.username:
                parser.error("--username is required when using --all")
            
            models_path = workspace_root / args.models_dir
            upload_all_models(
                models_dir=str(models_path),
                username=args.username,
                token=args.token,
                private=args.private
            )
        elif args.model:
            # Upload specific model
            if not args.repo:
                parser.error("--repo is required when using --model")
            
            model_path = workspace_root / args.model if not Path(args.model).is_absolute() else Path(args.model)
            upload_model_to_hf(
                model_path=str(model_path),
                repo_id=args.repo,
                token=args.token,
                private=args.private
            )
        else:
            parser.error("Either --all or --model must be specified")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
