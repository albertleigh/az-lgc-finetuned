#!/usr/bin/env python
"""
Fix Jupyter notebook widgets metadata for GitHub rendering.

This script removes the 'metadata.widgets' key from notebooks to fix
the GitHub rendering error: "the 'state' key is missing from 'metadata.widgets'"
"""
import json
import sys
from pathlib import Path


def fix_notebook(notebook_path: Path) -> bool:
    """
    Remove widgets metadata from a notebook file.
    
    Args:
        notebook_path: Path to the notebook file
        
    Returns:
        True if the notebook was modified, False otherwise
    """
    print(f"Processing: {notebook_path}")
    
    # Read the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Check if widgets metadata exists
    metadata = notebook.get('metadata', {})
    if 'widgets' not in metadata:
        print(f"  ✓ No widgets metadata found - skipping")
        return False
    
    # Remove the widgets metadata
    print(f"  → Removing widgets metadata...")
    del metadata['widgets']
    
    # Write back the notebook
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
        f.write('\n')  # Add trailing newline
    
    print(f"  ✓ Fixed!")
    return True


def main():
    # Get the project root (parent of scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    notebooks_dir = project_root / 'notebooks'
    
    if not notebooks_dir.exists():
        print(f"Error: Notebooks directory not found: {notebooks_dir}")
        sys.exit(1)
    
    # Find all notebook files
    notebook_files = list(notebooks_dir.glob('*.ipynb'))
    
    if not notebook_files:
        print(f"No notebook files found in {notebooks_dir}")
        sys.exit(0)
    
    print(f"Found {len(notebook_files)} notebook(s)\n")
    
    # Process each notebook
    modified_count = 0
    for notebook_path in sorted(notebook_files):
        if fix_notebook(notebook_path):
            modified_count += 1
        print()
    
    # Summary
    print("=" * 60)
    print(f"Summary: {modified_count}/{len(notebook_files)} notebook(s) modified")
    if modified_count > 0:
        print("\nYou can now commit and push the fixed notebooks to GitHub!")


if __name__ == '__main__':
    main()
