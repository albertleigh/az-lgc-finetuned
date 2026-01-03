"""
Example scripts for using the Logic App expression scrapers.
"""

import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers import GitHubLogicAppScraper, DatasetBuilder


def example_1_basic_scraping():
    """
    Example 1: Basic scraping of Logic App workflows.
    """
    print("=" * 60)
    print("Example 1: Basic Scraping")
    print("=" * 60)
    
    # Initialize scraper (will use GITHUB_TOKEN from .env if available)
    scraper = GitHubLogicAppScraper()
    
    # Check rate limits
    rate_info = scraper.get_rate_limit_info()
    print(f"\nGitHub API Rate Limits:")
    print(f"  Search remaining: {rate_info.get('search_remaining', 'N/A')}")
    print(f"  Core remaining: {rate_info.get('core_remaining', 'N/A')}")
    
    # Search for Logic App workflow files
    print("\nSearching for Logic App workflows...")
    files = scraper.search_logic_app_files(
        max_results=10,
        min_stars=5
    )
    
    print(f"\nFound {len(files)} workflow files:")
    for i, file in enumerate(files[:5], 1):
        print(f"  {i}. {file['repo_name']}/{file['file_path']}")
        print(f"     Stars: {file['repo_stars']}, URL: {file['url']}")


def example_2_search_by_expressions():
    """
    Example 2: Search for specific expression patterns.
    """
    print("\n" + "=" * 60)
    print("Example 2: Search by Expression Patterns")
    print("=" * 60)
    
    scraper = GitHubLogicAppScraper()
    
    # Common Logic App functions to search for
    patterns = ['concat', 'variables', 'triggerBody']
    
    print(f"\nSearching for patterns: {patterns}")
    files = scraper.search_by_expression_patterns(
        patterns=patterns,
        max_results=5
    )
    
    print(f"\nFound {len(files)} files with these patterns:")
    for file in files[:5]:
        print(f"  - {file['repo_name']}/{file['file_path']}")
        print(f"    Pattern: {file['search_pattern']}")


def example_3_full_dataset_pipeline():
    """
    Example 3: Complete pipeline - scrape, parse, and create dataset.
    """
    print("\n" + "=" * 60)
    print("Example 3: Full Dataset Creation Pipeline")
    print("=" * 60)
    
    # Initialize dataset builder
    builder = DatasetBuilder(output_dir="datasets")
    builder.initialize_scraper()
    
    # Step 1: Scrape workflows
    print("\nStep 1: Scraping workflows...")
    num_files = builder.scrape_workflows(
        max_files=20,
        min_stars=10
    )
    print(f"Scraped {num_files} workflow files")
    
    # Step 2: Download and parse
    print("\nStep 2: Downloading and parsing workflows...")
    num_workflows = builder.download_and_parse_workflows()
    print(f"Successfully parsed {num_workflows} workflows")
    
    # Step 3: Create training dataset
    print("\nStep 3: Creating training dataset...")
    num_samples = builder.create_training_dataset(
        min_quality_score=0.5,
        deduplicate=True
    )
    print(f"Created {num_samples} training samples")
    
    # Step 4: Generate statistics
    print("\nStep 4: Generating statistics...")
    report = builder.generate_statistics_report()
    
    print("\nDataset complete! Check the 'datasets' folder for output files.")


def example_4_parse_local_workflow():
    """
    Example 4: Parse a local Logic App workflow file.
    """
    print("\n" + "=" * 60)
    print("Example 4: Parse Local Workflow File")
    print("=" * 60)
    
    from scrapers import LogicAppExpressionParser
    
    # Sample workflow content
    sample_workflow = """
    {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "apiKey": {
                "type": "string"
            }
        },
        "triggers": {
            "When_a_HTTP_request_is_received": {
                "type": "Request",
                "kind": "Http",
                "inputs": {
                    "schema": {}
                }
            }
        },
        "actions": {
            "Initialize_userName": {
                "type": "InitializeVariable",
                "inputs": {
                    "variables": [{
                        "name": "userName",
                        "type": "string",
                        "value": "@{triggerBody()?['user']?['name']}"
                    }]
                }
            },
            "Initialize_greeting": {
                "type": "InitializeVariable",
                "inputs": {
                    "variables": [{
                        "name": "greeting",
                        "type": "string",
                        "value": "@{concat('Hello, ', variables('userName'), '!')}"
                    }]
                },
                "runAfter": {
                    "Initialize_userName": ["Succeeded"]
                }
            },
            "Compose_response": {
                "type": "Compose",
                "inputs": {
                    "message": "@{variables('greeting')}",
                    "timestamp": "@{formatDateTime(utcNow(), 'yyyy-MM-dd HH:mm:ss')}",
                    "apiKey": "@{parameters('apiKey')}"
                },
                "runAfter": {
                    "Initialize_greeting": ["Succeeded"]
                }
            }
        },
        "outputs": {}
    }
    """
    
    # Parse the workflow
    parser = LogicAppExpressionParser()
    
    print("\nChecking if content is a Logic App workflow...")
    is_workflow = parser.is_logic_app_workflow(sample_workflow)
    print(f"Is Logic App workflow: {is_workflow}")
    
    if is_workflow:
        print("\nParsing workflow...")
        workflow = parser.parse_workflow(sample_workflow)
        
        print("\nExtracting expressions...")
        expressions = parser.extract_all_expressions(workflow)
        
        print(f"\nFound {len(expressions)} expressions:")
        for i, expr in enumerate(expressions, 1):
            print(f"\n  Expression {i}:")
            print(f"    Raw: {expr['raw_expression']}")
            print(f"    Context: {expr['context']}")
            print(f"    Functions: {expr['functions_used']}")
            print(f"    Complexity: {expr['function_count']} functions, {expr['nesting_level']} nesting level")
        
        # Generate statistics
        print("\nExpression Statistics:")
        stats = parser.get_expression_statistics(expressions)
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Create training samples
        print("\nGenerating training samples:")
        for i, expr in enumerate(expressions[:3], 1):
            sample = parser.create_training_sample(expr)
            print(f"\n  Sample {i}:")
            print(f"    Natural Language: {sample['natural_language']}")
            print(f"    Expression: {sample['expression']}")


def example_5_search_repositories():
    """
    Example 5: Search for repositories containing Logic Apps.
    """
    print("\n" + "=" * 60)
    print("Example 5: Search Repositories")
    print("=" * 60)
    
    scraper = GitHubLogicAppScraper()
    
    # Search for repos with Logic App keywords
    keywords = ['azure-logic-apps', 'logic-app', 'workflow-definition']
    
    print(f"\nSearching repositories with keywords: {keywords}")
    repos = scraper.search_repositories(keywords, max_repos=10)
    
    print(f"\nFound {len(repos)} repositories:")
    for repo in repos[:10]:
        print(f"\n  {repo['full_name']}")
        print(f"    Stars: {repo['stars']}")
        print(f"    Description: {repo['description']}")
        print(f"    URL: {repo['url']}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Azure Logic App Expression Scraper - Examples")
    print("=" * 60)
    
    print("\nNote: These examples require a GitHub token for best results.")
    print("Create a .env file with GITHUB_TOKEN=your_token_here")
    print("Get a token at: https://github.com/settings/tokens")
    
    choice = input("\nWhich example would you like to run? (1-5, or 'all'): ").strip()
    
    if choice == '1':
        example_1_basic_scraping()
    elif choice == '2':
        example_2_search_by_expressions()
    elif choice == '3':
        example_3_full_dataset_pipeline()
    elif choice == '4':
        example_4_parse_local_workflow()
    elif choice == '5':
        example_5_search_repositories()
    elif choice.lower() == 'all':
        example_1_basic_scraping()
        example_2_search_by_expressions()
        example_4_parse_local_workflow()
        example_5_search_repositories()
        # Skip example 3 by default as it makes many API calls
        print("\n\nSkipping Example 3 (full pipeline) to avoid excessive API calls.")
        print("Run it separately if you want to create a full dataset.")
    else:
        print("Invalid choice. Please run again and select 1-5 or 'all'.")


if __name__ == '__main__':
    main()
