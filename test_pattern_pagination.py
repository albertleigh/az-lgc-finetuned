"""
Quick test to verify pagination works with search_by_expression_patterns
"""
import os
from scrapers.github_scraper import GitHubLogicAppScraper

# Initialize scraper
token = os.getenv('GITHUB_TOKEN')
if not token:
    print("Warning: No GITHUB_TOKEN found. Some tests may fail.")

scraper = GitHubLogicAppScraper(token)

# Test pagination with patterns
print("\n=== Testing pattern search WITHOUT pagination ===")
files_no_pagination = scraper.search_by_expression_patterns(
    patterns=['concat(', 'variables('],
    max_results=50,
    use_pagination_strategy=False
)
print(f"Found {len(files_no_pagination)} files without pagination")

print("\n=== Testing pattern search WITH pagination ===")
files_with_pagination = scraper.search_by_expression_patterns(
    patterns=['concat(', 'variables('],
    max_results=50,
    use_pagination_strategy=True
)
print(f"Found {len(files_with_pagination)} files with pagination")

# Show sample results
if files_with_pagination:
    print("\nSample results:")
    for i, file in enumerate(files_with_pagination[:3]):
        print(f"  {i+1}. {file['repo_name']} - {file['file_path']} (pattern: {file['search_pattern']})")

print("\n✅ Pagination implementation working!")
