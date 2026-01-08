# Getting Started with Azure Logic App Expression Scraper

## Quick Start (No GitHub Token Required)

To see the scraper in action immediately without any setup:

```bash
python demo.py
```

This will:
- Parse 10 sample Logic App expressions
- Extract and analyze a complete workflow
- Generate training samples
- Create a sample JSONL file in `datasets/demo_sample.jsonl`

## Full Setup for GitHub Scraping

### Step 1: Get a GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name like "Logic App Scraper"
4. Select scope: `public_repo`
5. Click "Generate token" and copy the token

### Step 2: Configure Your Environment

Edit the `.env` file in the project root:

```bash
GITHUB_TOKEN=ghp_your_token_here
```

### Step 3: Run Your First Scrape

Start with a small sample:

```bash
python scrape_logic_apps.py --max-files 20
```

This will:
1. Search GitHub for 20 Logic App workflow files
2. Download and parse them
3. Extract expressions
4. Create training datasets in multiple formats
5. Generate statistics

### Step 4: Check Your Results

Look in the `datasets/` folder:

```
datasets/
├── training_dataset_20260103_*.jsonl  # For fine-tuning
├── training_dataset_20260103_*.json   # Full data with metadata
├── training_dataset_20260103_*.csv    # For analysis
├── processed_workflows.json           # Parsed workflows
├── raw_files.json                     # Scraped file list
└── dataset_statistics.json            # Statistics report
```

## Command Line Options

```bash
# Scrape more files
python scrape_logic_apps.py --max-files 100

# Search for specific expression patterns (recommended for > 1000 files)
python scrape_logic_apps.py --max-files 2000 --patterns "concat(" "variables(" "triggerBody("

# Adjust quality threshold
python scrape_logic_apps.py --min-quality 0.5

# Keep duplicate expressions
python scrape_logic_apps.py --no-deduplicate

# Custom output directory
python scrape_logic_apps.py --output-dir my_dataset
```

## Using as a Python Library

### Example 1: Simple Scraping

```python
from scrapers import GitHubLogicAppScraper

scraper = GitHubLogicAppScraper()
files = scraper.search_logic_app_files(max_results=10)

for file in files:
    print(f"{file['repo_name']}: {file['file_path']}")
```

### Example 2: Parse Local Files

```python
from scrapers import LogicAppExpressionParser

parser = LogicAppExpressionParser()

with open('my_workflow.json') as f:
    workflow = parser.parse_workflow(f.read())
    expressions = parser.extract_all_expressions(workflow)
    
    for expr in expressions:
        print(expr['raw_expression'])
```

### Example 3: Full Pipeline

```python
from scrapers import DatasetBuilder

builder = DatasetBuilder(output_dir="my_dataset")
builder.initialize_scraper()

# Scrape workflows
builder.scrape_workflows(max_files=50)

# Parse and extract expressions
builder.download_and_parse_workflows()

# Create training dataset
builder.create_training_dataset(min_quality_score=0.5)

# Get statistics
report = builder.generate_statistics_report()
print(f"Created {report['total_samples']} training samples")
```

## Running Tests

```bash
# Run all tests
pytest tests/test_scrapers.py -v

# Run fast tests only (no network)
pytest tests/test_scrapers.py -v -k "not slow"

# Run with coverage
pytest tests/test_scrapers.py --cov=scrapers
```

## Interactive Examples

```bash
python examples/run_examples.py
```

Choose from:
1. Basic scraping
2. Search by expression patterns
3. Full dataset pipeline (makes many API calls)
4. Parse local workflow
5. Search repositories

## Understanding the Output

### JSONL Format (for fine-tuning)

```json
{
  "prompt": "Translate this natural language to Azure Logic App expression: concatenate strings using a workflow variable",
  "completion": "@{concat('Hello ', variables('userName'), '!')}"
}
```

### JSON Format (full data)

```json
{
  "natural_language": "concatenate strings using a workflow variable",
  "expression": "@{concat('Hello ', variables('userName'), '!')}",
  "functions": ["concat", "variables"],
  "context": "actions.Compose.inputs",
  "complexity": {
    "nesting_level": 2,
    "function_count": 2
  },
  "quality_score": 0.8,
  "metadata": {
    "source_repo": "user/repo",
    "source_file": "workflows/workflow.json",
    "repo_stars": 42
  }
}
```

## Tips for Best Results

### 1. Start Small
```bash
python scrape_logic_apps.py --max-files 20
```

### 2. Increase Gradually
```bash
python scrape_logic_apps.py --max-files 100
python scrape_logic_apps.py --max-files 500
python scrape_logic_apps.py --max-files 1000
```

### 3. Use Patterns for Large Datasets (> 1000 files)
```bash
# Exceeds single-query limit via multiple pattern searches
python scrape_logic_apps.py --max-files 2000 --patterns "concat(" "variables(" "parameters("
# Or let the script auto-select patterns
python scrape_logic_apps.py --max-files 2000
```

### 4. Target Specific Patterns
```bash
# Focus on common functions
python scrape_logic_apps.py --max-files 500 --patterns "concat(" "variables(" "triggerBody("
```

### 5. Analyze Your Data
```python
# Open the CSV in Excel or pandas
import pandas as pd
df = pd.read_csv('datasets/training_dataset_*.csv')
print(df['functions'].value_counts())
```

## Rate Limits

### Without Token
- Search: 10 requests/minute
- Core: 60 requests/hour
- **Recommendation**: Only for quick testing with < 20 files

### With Token
- Search: 30 requests/minute  
- Core: 5,000 requests/hour
- **Recommendation**: Required for serious dataset collection

**Note**: Each pattern search uses 1 search API request. Using 3 patterns = 3 requests.

## Troubleshooting

### Problem: "Requires authentication" error
**Solution**: Add GitHub token to `.env` file

### Problem: Rate limit exceeded
**Solution**: 
- Wait a few minutes
- Use a GitHub token
- Reduce `--max-files`

### Problem: No workflows found
**Solution**:
- Check your internet connection
- Verify GitHub token is set in `.env` file
- Try a smaller `--max-files` value first

### Problem: Low quality samples
**Solution**:
- Lower `--min-quality` (try 0.0 to include all)
- Increase `--max-files` for more variety
- Use `--patterns` to target specific expression types

### Problem: Too many duplicates
**Solution**: Deduplication is on by default, but if you still see many:
- Increase `--max-files` to get more unique repos
- Use diverse `--patterns` to get varied expressions
- Note: Some duplication is normal across popular Logic App patterns

## Next Steps: Fine-Tuning

Once you have a dataset:

1. **Review the CSV** - Inspect quality and coverage
2. **Augment if needed** - Add better natural language descriptions
3. **Split the data** - Train/validation/test sets
4. **Format for your model** - Adapt JSONL to your model's requirements
5. **Fine-tune** - Use with Salesforce/codegen-350M-mono or similar

### Example: Preparing for Codegen

```python
import json

# Read your dataset
with open('datasets/training_dataset_*.jsonl') as f:
    samples = [json.loads(line) for line in f]

# Format for your model
formatted = []
for sample in samples:
    formatted.append({
        'text': f"{sample['prompt']}\n\n{sample['completion']}<|endoftext|>"
    })

# Save
with open('codegen_training.jsonl', 'w') as f:
    for item in formatted:
        f.write(json.dumps(item) + '\n')
```

## Support

For issues or questions:
1. Check the README.md for documentation
2. Review the examples in `examples/run_examples.py`
3. Run the tests: `pytest tests/ -v`
4. Check GitHub API status: https://www.githubstatus.com/
