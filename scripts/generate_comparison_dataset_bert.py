"""
Generate comparison dataset for BERT model training.
This script creates a binary classification dataset to train a model
that can distinguish Azure Logic App expressions from other code expressions.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from datasets import load_dataset
from typing import List, Dict


def load_cpp_fortran_expressions() -> List[str]:
    """Load all CPP and Fortran expressions from the NLP-CPP-Fortran dataset."""
    print("Loading NLP-CPP-Fortran dataset...")
    dataset = load_dataset("Bin12345/NLP-CPP-Fortran", split="train")
    
    expressions = []
    for row in dataset:
        # Add CPP expressions if they exist
        if row.get('CPP'):
            expressions.append(str(row['CPP']))
        # Add Fortran expressions if they exist
        if row.get('Fortran'):
            expressions.append(str(row['Fortran']))
    
    print(f"Loaded {len(expressions)} CPP/Fortran expressions")
    return expressions


def load_sql_expressions(sample_size: int = 5811) -> List[str]:
    """Load and randomly sample SQL expressions."""
    print(f"Loading SQL dataset (sampling {sample_size} rows)...")
    dataset = load_dataset("Aditya011/autotrain-data-nl-to-sql", split="train")
    
    # Get total size
    total_size = len(dataset)
    print(f"Total SQL dataset size: {total_size}")
    
    # Sample randomly
    if total_size > sample_size:
        indices = random.sample(range(total_size), sample_size)
        sampled_dataset = dataset.select(indices)
    else:
        sampled_dataset = dataset
        print(f"Warning: Dataset has only {total_size} rows, using all")
    
    expressions = []
    for row in sampled_dataset:
        if row.get('sql'):
            expressions.append(str(row['sql']))
    
    print(f"Loaded {len(expressions)} SQL expressions")
    return expressions


def load_javascript_expressions(sample_size: int = 5811) -> List[str]:
    """Load and randomly sample JavaScript expressions."""
    print(f"Loading JavaScript dataset (sampling {sample_size} rows)...")
    dataset = load_dataset("semeru/code-text-javascript", split="train")
    
    # Get total size
    total_size = len(dataset)
    print(f"Total JavaScript dataset size: {total_size}")
    
    # Sample randomly
    if total_size > sample_size:
        indices = random.sample(range(total_size), sample_size)
        sampled_dataset = dataset.select(indices)
    else:
        sampled_dataset = dataset
        print(f"Warning: Dataset has only {total_size} rows, using all")
    
    expressions = []
    for row in sampled_dataset:
        if row.get('original_string'):
            expressions.append(str(row['original_string']))
    
    print(f"Loaded {len(expressions)} JavaScript expressions")
    return expressions


def load_logic_app_expressions(file_path: str) -> List[str]:
    """Load Azure Logic App expressions from existing dataset."""
    print(f"Loading Logic App expressions from {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    expressions = []
    for item in data:
        if item.get('expression'):
            expressions.append(str(item['expression']))
    
    print(f"Loaded {len(expressions)} Logic App expressions")
    return expressions


def create_comparison_dataset(
    non_logic_expressions: List[str],
    logic_expressions: List[str]
) -> List[Dict[str, any]]:
    """Create the comparison dataset with expression and complete flag."""
    dataset = []
    
    # Add non-Logic App expressions (complete=False)
    for expr in non_logic_expressions:
        dataset.append({
            "expression": expr,
            "complete": False
        })
    
    # Add Logic App expressions (complete=True)
    for expr in logic_expressions:
        dataset.append({
            "expression": expr,
            "complete": True
        })
    
    # Shuffle the dataset
    random.shuffle(dataset)
    
    return dataset


def main():
    """Main execution function."""
    # Set random seed for reproducibility
    random.seed(42)
    
    print("=" * 60)
    print("Generating Comparison Dataset for BERT Model Training")
    print("=" * 60)
    print()
    
    # Load non-Logic App expressions
    non_logic_expressions = []
    
    # 1. Load CPP and Fortran expressions
    try:
        cpp_fortran = load_cpp_fortran_expressions()
        non_logic_expressions.extend(cpp_fortran)
    except Exception as e:
        print(f"Error loading CPP/Fortran dataset: {e}")
    
    print()
    
    # 2. Load SQL expressions
    try:
        sql = load_sql_expressions(sample_size=5811)
        non_logic_expressions.extend(sql)
    except Exception as e:
        print(f"Error loading SQL dataset: {e}")
    
    print()
    
    # 3. Load JavaScript expressions
    try:
        javascript = load_javascript_expressions(sample_size=5811)
        non_logic_expressions.extend(javascript)
    except Exception as e:
        print(f"Error loading JavaScript dataset: {e}")
    
    print()
    
    print(f"Total non-Logic App expressions: {len(non_logic_expressions)}")
    print()
    
    # 4. Load Logic App expressions
    logic_app_file = Path("datasets/training_dataset_20260104_125624.json")
    
    if not logic_app_file.exists():
        print(f"Error: File not found: {logic_app_file}")
        return
    
    logic_expressions = load_logic_app_expressions(str(logic_app_file))
    print()
    
    # Create comparison dataset
    print("Creating comparison dataset...")
    comparison_dataset = create_comparison_dataset(
        non_logic_expressions,
        logic_expressions
    )
    
    print(f"Total dataset size: {len(comparison_dataset)}")
    print(f"  - Logic App expressions (complete=True): {len(logic_expressions)}")
    print(f"  - Non-Logic App expressions (complete=False): {len(non_logic_expressions)}")
    print()
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(f"datasets/compare_training_dataset_{timestamp}.json")
    
    print(f"Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_dataset, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 60)
    print("Dataset generation complete!")
    print(f"Output file: {output_file}")
    print("=" * 60)
    
    # Print some statistics
    print()
    print("Sample entries:")
    for i, entry in enumerate(comparison_dataset[:5]):
        expr_preview = entry['expression'][:80] + "..." if len(entry['expression']) > 80 else entry['expression']
        print(f"{i+1}. [{entry['complete']}] {expr_preview}")


if __name__ == "__main__":
    main()
