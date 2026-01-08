# Azure Logic App Expression Scraper

A reusable Python toolkit for scraping Azure Logic App expressions from GitHub repositories to create fine-tuning datasets for code generation models.

## Overview

This project helps you collect Azure Logic App workflow expressions from public GitHub repositories to build a dataset for fine-tuning models like Salesforce/codegen-350M-mono. The dataset pairs natural language descriptions with corresponding Logic App expressions.

## Features

- 🔍 **GitHub Scraping**: Search and download Logic App workflow files from GitHub
- 🔧 **Expression Parsing**: Extract and analyze Logic App expressions from workflow definitions
- 📊 **Dataset Building**: Create structured training datasets in multiple formats (JSON, JSONL, CSV)
- 🧪 **Quality Scoring**: Automatic quality assessment of expressions based on complexity and source
- 📈 **Statistics**: Generate comprehensive reports about your dataset
- ✅ **Testing**: Full test suite for validation

## Project Structure

```
az-lgc-finetuned/
├── scrapers/
│   ├── __init__.py
│   ├── github_scraper.py       # GitHub API scraping functionality
│   ├── expression_parser.py    # Logic App expression parser
│   └── dataset_builder.py      # Dataset creation pipeline
├── tests/
│   ├── __init__.py
│   └── test_scrapers.py        # Test suite
├── examples/
│   └── run_examples.py         # Usage examples
├── datasets/                   # Output directory (created automatically)
├── scrape_logic_apps.py        # Main CLI script
├── requirements.txt
└── README.md
```

## Installation

1. **Clone or set up the project directory**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up GitHub token** (recommended for higher API rate limits):
   - Create a personal access token at https://github.com/settings/tokens
   - Create a `.env` file in the project root:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```

## Quick Start

### Option 1: Run the Full Pipeline

```bash
python scrape_logic_apps.py --max-files 50 --min-stars 5
```

This will:
1. Search GitHub for Logic App workflow files
2. Download and parse them
3. Extract expressions
4. Create training datasets
5. Generate statistics

### Option 2: Use the Examples

```bash
python examples/run_examples.py
```

Choose from interactive examples demonstrating different features.

### Option 3: Use as a Library

```python
from scrapers import DatasetBuilder

# Initialize and run pipeline
builder = DatasetBuilder(output_dir="datasets")
builder.initialize_scraper()

# Scrape workflows
builder.scrape_workflows(max_files=100, min_stars=10)

# Parse and create dataset
builder.download_and_parse_workflows()
builder.create_training_dataset(min_quality_score=0.5)
builder.generate_statistics_report()
```

## CLI Options

```bash
python scrape_logic_apps.py [OPTIONS]

Options:
  --max-files INT       Maximum files to scrape (default: 100)
  --min-stars INT       Minimum repo stars (default: 5)
  --min-quality FLOAT   Minimum quality score (default: 0.5)
  --output-dir PATH     Output directory (default: datasets)
  --no-deduplicate      Keep duplicate expressions
  --patterns [LIST]     Specific patterns to search (e.g., concat variables)
```

## Output Files

The scraper generates several output files in the `datasets/` directory:

- **`training_dataset_*.jsonl`**: JSONL format for fine-tuning (prompt/completion pairs)
- **`training_dataset_*.json`**: Complete dataset with all metadata
- **`training_dataset_*.csv`**: CSV format for analysis in Excel/Pandas
- **`processed_workflows.json`**: Parsed workflow data
- **`raw_files.json`**: List of scraped files
- **`dataset_statistics.json`**: Statistics report

### Example JSONL Format

```json
{"prompt": "Translate this natural language to Azure Logic App expression: In an action, concatenate strings using a workflow variable", "completion": "@{concat('Hello, ', variables('userName'), '!')}"}
```

## Usage Examples

### Example 1: Search for Specific Patterns

```python
from scrapers import GitHubLogicAppScraper

scraper = GitHubLogicAppScraper()
files = scraper.search_by_expression_patterns(
    patterns=['concat', 'variables', 'triggerBody'],
    max_results=50
)
```

### Example 2: Parse a Local Workflow

```python
from scrapers import LogicAppExpressionParser

parser = LogicAppExpressionParser()

with open('workflow.json', 'r') as f:
    content = f.read()

workflow = parser.parse_workflow(content)
expressions = parser.extract_all_expressions(workflow)

for expr in expressions:
    print(f"Expression: {expr['raw_expression']}")
    print(f"Functions: {expr['functions_used']}")
```

### Example 3: Custom Dataset Creation

```python
from scrapers import DatasetBuilder

builder = DatasetBuilder(output_dir="my_dataset")
builder.initialize_scraper()

# Load existing scraped data
builder.load_existing_data("datasets/raw_files.json")

# Create dataset with custom settings
builder.create_training_dataset(
    min_quality_score=0.7,
    deduplicate=True
)
```

## Testing

Run the test suite:

```bash
pytest tests/test_scrapers.py -v
```

Run specific test categories:

```bash
# Fast tests only (no network calls)
pytest tests/test_scrapers.py -v -m "not slow"

# Include integration tests
pytest tests/test_scrapers.py -v --runintegration
```

## Azure Logic App Expressions

This scraper recognizes and parses various Logic App expression patterns:

### Expression Syntax
- `@{expression}` - Standard expression syntax
- `@function()` - Direct function calls

### Common Functions Supported
- **String**: `concat`, `substring`, `replace`, `toLower`, `toUpper`, `trim`, `split`, `join`
- **Math**: `add`, `sub`, `mul`, `div`, `mod`, `min`, `max`
- **Logic**: `if`, `equals`, `not`, `and`, `or`, `greater`, `less`
- **Data**: `variables`, `parameters`, `triggerBody`, `body`, `outputs`
- **Date/Time**: `formatDateTime`, `utcNow`, `addDays`, `addHours`
- **Conversion**: `string`, `int`, `json`, `base64`
- **Arrays**: `first`, `last`, `take`, `skip`, `createArray`

### Example Expressions

```javascript
// String concatenation with variable
@{concat('Hello, ', variables('userName'), '!')}

// Conditional logic
@{if(equals(variables('status'), 'active'), 'Active User', 'Inactive User')}

// Access trigger data
@{triggerBody()?['user']?['email']}

// Date formatting
@{formatDateTime(utcNow(), 'yyyy-MM-dd HH:mm:ss')}

// Nested functions
@{concat(toUpper(substring(variables('name'), 0, 1)), toLower(substring(variables('name'), 1)))}
```

## Rate Limits

GitHub API rate limits (without token):
- **Search**: 10 requests per minute
- **Core**: 60 requests per hour

With an authenticated token:
- **Search**: 30 requests per minute
- **Core**: 5,000 requests per hour

The scraper includes automatic rate limit handling and will wait when limits are reached.

## Tips for Best Results

1. **Use a GitHub token**: Significantly higher rate limits
2. **Start small**: Test with `--max-files 10` first
3. **Filter by stars**: Use `--min-stars 10` to get higher quality repos
4. **Search specific patterns**: Use `--patterns concat variables` to target specific expressions
5. **Adjust quality threshold**: Lower `--min-quality` to get more samples
6. **Review the CSV**: Inspect `training_dataset_*.csv` to understand your data

## Fine-Tuning Next Steps

After creating your dataset:

1. **Review the data**: Open the CSV file to inspect quality
2. **Augment descriptions**: Enhance natural language descriptions if needed
3. **Balance the dataset**: Ensure good coverage of different expression types
4. **Format for your model**: Adapt the JSONL format to your specific model requirements
5. **Fine-tune**: Use the dataset with your chosen model (e.g., Salesforce/codegen-350M-mono)

## Trained Models

This project includes two pre-trained models:

### BERT Classifier
- **Purpose**: Classify if text is an Azure Logic App expression
- **Model**: `albertleigh/azlgc-bert-classifier` (HuggingFace)
- **Accuracy**: ~95-98% on test set
- **Usage**: `python clis/run_bert_model.py`

### GPT-2 Generator
- **Purpose**: Generate Logic App expressions from natural language
- **Model**: `albertleigh/azlgc-gpt` (HuggingFace)
- **Usage**: `python clis/run_gpt_model.py`

**See [docs/CLI_USAGE.md](docs/CLI_USAGE.md)** for complete CLI documentation.

## Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Step-by-step beginner's guide
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Detailed project organization
- **[Pagination](docs/PAGINATION.md)** - Collecting large datasets (>1000 files)
- **[CLI Usage](docs/CLI_USAGE.md)** - Using BERT classifier and GPT generator
- **[Model Training](docs/MODEL_TRAINING.md)** - Training models with Jupyter notebooks

## Troubleshooting

### Rate Limit Errors
- Add a GitHub token to `.env`
- Reduce `--max-files`
- Wait between runs

### No Workflows Found
- Lower `--min-stars`
- Remove `--patterns` to search more broadly
- Check your internet connection

### Low Quality Samples
- Lower `--min-quality`
- Increase `--max-files` to get more variety
- Search in repos with more stars

## Contributing

This is a reusable toolkit. Feel free to extend it:
- Add more expression pattern matching
- Improve natural language generation
- Add support for other Logic App features
- Enhance quality scoring algorithms

## License

This project is for educational and research purposes. Respect GitHub's terms of service and API usage guidelines.

## Acknowledgments

Similar to SQL expression scraping projects but adapted for Azure Logic Apps workflow expressions.
