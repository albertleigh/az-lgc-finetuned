"""Test the ARM template parsing."""
from scrapers import GitHubLogicAppScraper, LogicAppExpressionParser

scraper = GitHubLogicAppScraper()
parser = LogicAppExpressionParser()

# Test with the ARM template file
file_info = {
    'repo_name': 'aliencube/ARM-Deployment-History-Cleaner',
    'file_path': 'LogicApp.json',
    'download_url': 'https://raw.githubusercontent.com/aliencube/ARM-Deployment-History-Cleaner/9883e2ce73cb42073c09e8fc0c6f002e5a293b5c/LogicApp.json'
}

content = scraper.download_file_content(file_info)
print(f"Downloaded {len(content)} bytes")

is_workflow = parser.is_logic_app_workflow(content)
print(f"Is Logic App: {is_workflow}")

if is_workflow:
    workflow = parser.parse_workflow(content)
    expressions = parser.extract_all_expressions(workflow)
    print(f"\nFound {len(expressions)} expressions:")
    for i, expr in enumerate(expressions[:10], 1):
        print(f"  {i}. {expr['raw_expression'][:100]}")
