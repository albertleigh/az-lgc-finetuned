# Project Structure

## Complete File Tree

```
az-lgc-finetuned/
│
├── .env                          # Your GitHub token (create from .env.example)
├── .env.example                  # Template for environment variables
├── .gitignore                    # Git ignore patterns
├── requirements.txt              # Python dependencies
├── README.md                     # Main documentation
├── GETTING_STARTED.md            # Quick start guide
├── PROJECT_STRUCTURE.md          # This file
│
├── demo.py                       # Quick demo (no token required) ⭐ START HERE
├── scrape_logic_apps.py          # Main CLI script for scraping
│
├── scrapers/                     # Core scraping modules
│   ├── __init__.py               # Package initialization
│   ├── github_scraper.py         # GitHub API integration
│   ├── expression_parser.py      # Logic App expression parser
│   └── dataset_builder.py        # Dataset creation pipeline
│
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_scrapers.py          # Comprehensive tests
│
├── examples/                     # Usage examples
│   └── run_examples.py           # Interactive examples script
│
└── datasets/                     # Output directory (auto-created)
    ├── demo_sample.jsonl         # Demo output
    ├── raw_files.json            # List of scraped files
    ├── processed_workflows.json  # Parsed workflow data
    ├── training_dataset_*.jsonl  # Training data (JSONL format)
    ├── training_dataset_*.json   # Training data (full JSON)
    ├── training_dataset_*.csv    # Training data (CSV for analysis)
    └── dataset_statistics.json   # Dataset statistics report
```

## Key Files Explained

### Entry Points

| File | Purpose | When to Use |
|------|---------|-------------|
| `demo.py` | Quick demonstration without GitHub token | First time, to understand how it works |
| `scrape_logic_apps.py` | Full scraping pipeline from GitHub | When you have a token and want real data |
| `examples/run_examples.py` | Interactive examples | To learn different features |

### Core Modules

| Module | Contains | Purpose |
|--------|----------|---------|
| `scrapers/github_scraper.py` | `GitHubLogicAppScraper` | Search and download Logic App files from GitHub |
| `scrapers/expression_parser.py` | `LogicAppExpressionParser` | Extract and analyze Logic App expressions |
| `scrapers/dataset_builder.py` | `DatasetBuilder` | Orchestrate scraping and dataset creation |

### Configuration

| File | Purpose |
|------|---------|
| `.env` | Your GitHub personal access token |
| `.env.example` | Template to create .env |
| `requirements.txt` | Python package dependencies |

### Documentation

| File | Content |
|------|---------|
| `README.md` | Comprehensive documentation, features, examples |
| `GETTING_STARTED.md` | Step-by-step guide for beginners |
| `PROJECT_STRUCTURE.md` | This file - project organization |

## Module Details

### scrapers/github_scraper.py

**Classes:**
- `GitHubLogicAppScraper` - Main scraper class

**Key Methods:**
- `search_logic_app_files()` - Search for workflow files
- `search_by_expression_patterns()` - Search by specific expressions
- `download_file_content()` - Download file from GitHub
- `search_repositories()` - Find repos with Logic Apps
- `get_rate_limit_info()` - Check API rate limits

**Dependencies:**
- PyGithub - GitHub API wrapper
- requests - HTTP client
- python-dotenv - Environment variables

### scrapers/expression_parser.py

**Classes:**
- `LogicAppExpressionParser` - Parse Logic App expressions

**Key Methods:**
- `is_logic_app_workflow()` - Detect workflow files
- `parse_workflow()` - Parse JSON workflow
- `extract_all_expressions()` - Find all expressions in workflow
- `analyze_expression()` - Analyze single expression
- `get_expression_statistics()` - Generate stats
- `create_training_sample()` - Create ML training sample
- `generate_expression_descriptions()` - Generate NL descriptions

**No External Dependencies** (uses only Python stdlib)

### scrapers/dataset_builder.py

**Classes:**
- `DatasetBuilder` - Complete pipeline orchestrator

**Key Methods:**
- `initialize_scraper()` - Set up GitHub scraper
- `scrape_workflows()` - Scrape from GitHub
- `download_and_parse_workflows()` - Process workflows
- `create_training_dataset()` - Generate training data
- `generate_statistics_report()` - Create report
- `load_existing_data()` - Load previous results

**Dependencies:**
- pandas - Data manipulation
- tqdm - Progress bars

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Logic App Scraper                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │      Choose Entry Point                   │
        └───────────────────────────────────────────┘
                │                │                 │
                ▼                ▼                 ▼
         ┌──────────┐    ┌────────────┐    ┌──────────┐
         │ demo.py  │    │ scrape_    │    │examples/ │
         │ (no API) │    │logic_apps  │    │run_      │
         │          │    │.py (API)   │    │examples  │
         └──────────┘    └────────────┘    └──────────┘
                │                │
                └────────┬───────┘
                         ▼
        ┌─────────────────────────────────────────┐
        │     GitHubLogicAppScraper               │
        │  • Search GitHub for workflow files     │
        │  • Download file content                │
        │  • Handle rate limits                   │
        └─────────────────────────────────────────┘
                         │
                         ▼
        ┌─────────────────────────────────────────┐
        │    LogicAppExpressionParser             │
        │  • Parse workflow JSON                  │
        │  • Extract expressions                  │
        │  • Analyze complexity                   │
        └─────────────────────────────────────────┘
                         │
                         ▼
        ┌─────────────────────────────────────────┐
        │         DatasetBuilder                  │
        │  • Orchestrate pipeline                 │
        │  • Score quality                        │
        │  • Generate datasets                    │
        │  • Create statistics                    │
        └─────────────────────────────────────────┘
                         │
                         ▼
        ┌─────────────────────────────────────────┐
        │          Output Files                   │
        │  • training_dataset_*.jsonl (ML ready)  │
        │  • training_dataset_*.json (full data)  │
        │  • training_dataset_*.csv (analysis)    │
        │  • processed_workflows.json             │
        │  • dataset_statistics.json              │
        └─────────────────────────────────────────┘
```

## Data Flow

```
GitHub Repository
        ↓
    [Search API]
        ↓
   File Metadata → raw_files.json
        ↓
  [Download Content]
        ↓
    Workflow JSON
        ↓
  [Parse & Extract]
        ↓
   Expressions List
        ↓
  [Analyze & Score]
        ↓
  Training Samples → processed_workflows.json
        ↓
  [Format & Save]
        ↓
    ┌──────┴──────┬──────────────┐
    ↓             ↓              ↓
  .jsonl        .json          .csv
  (ML)        (Full)      (Analysis)
```

## Testing Structure

```
tests/
└── test_scrapers.py
    ├── TestLogicAppExpressionParser
    │   ├── test_simple_expression_extraction
    │   ├── test_nested_expression
    │   ├── test_workflow_detection
    │   ├── test_extract_from_workflow
    │   ├── test_expression_statistics
    │   ├── test_training_sample_creation
    │   └── test_complex_expression
    │
    ├── TestGitHubScraper
    │   ├── test_scraper_initialization
    │   ├── test_rate_limit_info
    │   └── test_search_logic_app_files (slow)
    │
    ├── TestIntegration
    │   └── test_sample_workflow_parsing
    │
    └── test_expression_patterns
```

## Output Format Comparison

### JSONL (for fine-tuning)
```jsonl
{"prompt": "...", "completion": "@{...}"}
```
- One sample per line
- Easy to stream
- Compatible with most ML frameworks
- Best for: Training models

### JSON (complete data)
```json
[{
  "natural_language": "...",
  "expression": "@{...}",
  "functions": [...],
  "complexity": {...},
  "quality_score": 0.8,
  "metadata": {...}
}]
```
- Full structure
- All metadata
- Easy to read
- Best for: Understanding, debugging, filtering

### CSV (for analysis)
```csv
natural_language,expression,functions,context,quality_score,...
```
- Spreadsheet compatible
- Easy filtering/sorting
- Quick statistics
- Best for: Excel, pandas, data analysis

## Dependencies

### Required
```
requests>=2.31.0        # HTTP client
PyGithub>=2.1.1         # GitHub API
beautifulsoup4>=4.12.0  # HTML parsing (if needed)
python-dotenv>=1.0.0    # Environment variables
pandas>=2.1.0           # Data manipulation
tqdm>=4.66.0            # Progress bars
```

### Development
```
pytest>=7.4.0           # Testing framework
```

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GITHUB_TOKEN` | Recommended | None | GitHub API authentication |

## API Rate Limits

| Endpoint | Without Token | With Token |
|----------|---------------|------------|
| Search | 10/min | 30/min |
| Core | 60/hour | 5000/hour |

## File Size Guide

| Dataset Size | Files | Expected Output |
|--------------|-------|-----------------|
| Small | 10-20 | ~50-200 samples, <1 MB |
| Medium | 50-100 | ~200-1000 samples, 1-5 MB |
| Large | 200-500 | ~1000-5000 samples, 5-25 MB |
| Extra Large | 1000+ | ~5000+ samples, 25+ MB |

## Quick Reference

### Run Demo
```bash
python demo.py
```

### Run Tests
```bash
pytest tests/ -v
```

### Scrape Small Dataset
```bash
python scrape_logic_apps.py --max-files 20
```

### Scrape Large Dataset
```bash
python scrape_logic_apps.py --max-files 500 --min-stars 10
```

### Use as Library
```python
from scrapers import DatasetBuilder
builder = DatasetBuilder()
builder.initialize_scraper()
builder.scrape_workflows(max_files=50)
builder.download_and_parse_workflows()
builder.create_training_dataset()
```
