"""
Diagnostic script to inspect downloaded workflow files and understand why they're being skipped.
"""

import json
from pathlib import Path
from scrapers import load_results, LogicAppExpressionParser

def diagnose_raw_files():
    """Inspect the raw_files.json to see what was downloaded."""
    
    raw_files_path = Path("datasets/raw_files.json")
    
    if not raw_files_path.exists():
        print("❌ datasets/raw_files.json not found. Run the scraper first.")
        return
    
    files = load_results(str(raw_files_path))
    parser = LogicAppExpressionParser()
    
    print(f"=== Diagnosing {len(files)} Downloaded Files ===\n")
    
    # Import the scraper to download content
    from scrapers import GitHubLogicAppScraper
    scraper = GitHubLogicAppScraper()
    
    for i, file_info in enumerate(files[:10], 1):  # Check first 10 files
        print(f"\n{'='*70}")
        print(f"File {i}: {file_info['repo_name']}/{file_info['file_path']}")
        print(f"Stars: {file_info.get('repo_stars', 0)}")
        print(f"URL: {file_info['url']}")
        print(f"{'='*70}")
        
        # Download content
        content = scraper.download_file_content(file_info)
        
        if not content:
            print("❌ Failed to download content")
            continue
        
        # Parse JSON
        try:
            data = json.loads(content)
            print(f"\n✅ Valid JSON")
            print(f"Size: {len(content)} bytes")
            print(f"\nTop-level keys: {list(data.keys())[:10]}")
            
            # Check for Logic App indicators
            print(f"\n🔍 Logic App Indicators:")
            print(f"  - Has '$schema': {'$schema' in data}")
            if '$schema' in data:
                print(f"    Schema: {data['$schema']}")
            print(f"  - Has 'definition': {'definition' in data}")
            if 'definition' in data:
                print(f"    Definition keys: {list(data['definition'].keys())[:10] if isinstance(data['definition'], dict) else 'Not a dict'}")
            print(f"  - Has 'actions': {'actions' in data}")
            if 'actions' in data:
                action_type = type(data['actions']).__name__
                print(f"    Actions type: {action_type}")
                if isinstance(data['actions'], dict):
                    print(f"    Actions count: {len(data['actions'])}")
                    print(f"    Action names: {list(data['actions'].keys())[:5]}")
                elif isinstance(data['actions'], list):
                    print(f"    Actions count: {len(data['actions'])}")
            print(f"  - Has 'triggers': {'triggers' in data}")
            if 'triggers' in data:
                trigger_type = type(data['triggers']).__name__
                print(f"    Triggers type: {trigger_type}")
            print(f"  - Has 'contentVersion': {'contentVersion' in data}")
            print(f"  - Has 'parameters': {'parameters' in data}")
            
            # Test detection
            is_workflow = parser.is_logic_app_workflow(content)
            print(f"\n{'✅' if is_workflow else '❌'} Detected as Logic App workflow: {is_workflow}")
            
            if is_workflow:
                # Try to extract expressions
                workflow = parser.parse_workflow(content)
                if workflow:
                    expressions = parser.extract_all_expressions(workflow)
                    print(f"📊 Found {len(expressions)} expressions")
                    if expressions:
                        print(f"\nFirst few expressions:")
                        for j, expr in enumerate(expressions[:3], 1):
                            print(f"  {j}. {expr['raw_expression'][:80]}...")
                    else:
                        print("⚠️  No expressions found in workflow")
            else:
                print("\n⚠️  File not recognized as Logic App workflow")
                print("\nSample content (first 500 chars):")
                print(json.dumps(data, indent=2)[:500] + "...")
        
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n{'='*70}")
    print("Diagnosis complete!")
    print(f"{'='*70}")


if __name__ == '__main__':
    diagnose_raw_files()
