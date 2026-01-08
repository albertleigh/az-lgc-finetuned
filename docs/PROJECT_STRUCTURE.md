# Project Structure

## Complete File Tree

```
az-lgc-finetuned/
│
├── .env                          # Your GitHub token (create from .env.example)
├── .env.example                  # Template for environment variables
├── .gitignore                    # Git ignore patterns
├── requirements.txt              # Python dependencies
├── requirements-clis.txt         # CLI tool dependencies
├── README.md                     # Main documentation
├── CHANGELOG.md                  # Project changelog
│
├── demo.py                       # Quick demo (no token required) ⭐ START HERE
├── scrape_logic_apps.py          # Main CLI script for scraping
├── diagnose.py                   # Diagnostic utilities
├── test_*.py                     # Test scripts
│
├── clis/                         # CLI tools for trained models
│   ├── run_bert_model.py         # BERT classifier CLI
│   └── run_gpt_model.py          # GPT generator CLI
│
├── scrapers/                     # Core scraping modules
│   ├── __init__.py               # Package initialization
│   ├── github_scraper.py         # GitHub API integration
│   ├── expression_parser.py      # Logic App expression parser
│   └── dataset_builder.py        # Dataset creation pipeline
│
├── notebooks/                    # Training notebooks
│   ├── az_lgc_exp_catagory_bert.ipynb  # BERT classifier training
│   └── az_lgc_exp_gpt2.ipynb           # GPT-2 generator training
│
├── models/                       # Trained model files
│   ├── bert_classifier_azlgcexp_base/  # BERT classifier (local)
│   └── azLgcExpGpt_HF/                 # GPT-2 generator (local)
│
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_scrapers.py          # Comprehensive tests
│
├── examples/                     # Usage examples
│   └── run_examples.py           # Interactive examples script
│
├── scripts/                      # Utility scripts
│   ├── check_parquet.py
│   ├── combine_training_datasets.py
│   ├── convert_json_to_parquet.py
│   ├── generate_comparison_dataset_bert.py
│   ├── upload_models_to_hf.py
│   ├── upload_to_huggingface.py
│   └── README.md
│
├── docs/                         # Documentation
│   ├── GETTING_STARTED.md        # Quick start guide
│   ├── PROJECT_STRUCTURE.md      # This file
│   ├── PAGINATION.md             # Pagination feature docs
│   ├── CLI_USAGE.md              # CLI tools documentation
│   └── MODEL_TRAINING.md         # Notebook training guide
│
├── datasets/                     # Output directory (auto-created)
│   ├── demo_sample.jsonl         # Demo output
│   ├── raw_files.json            # List of scraped files
│   ├── processed_workflows.json  # Parsed workflow data
│   ├── training_dataset_*.jsonl  # Training data (JSONL format)
│   ├── training_dataset_*.json   # Training data (full JSON)
│   ├── training_dataset_*.csv    # Training data (CSV for analysis)
│   ├── dataset_statistics.json   # Dataset statistics report
│   └── updated/                  # Updated datasets
│
└── workflows/                    # Workflow utilities
    └── complete_natural_language.py
```

## Key Files Explained

### Entry Points

| File | Purpose | When to Use |
|------|---------|-------------|
| `demo.py` | Quick demonstration without GitHub token | First time, to understand how it works |
| `scrape_logic_apps.py` | Full scraping pipeline from GitHub | When you have a token and want real data |
| `examples/run_examples.py` | Interactive examples | To learn different features |
| `clis/run_bert_model.py` | BERT classifier CLI | Classify if text is Logic App expression |
| `clis/run_gpt_model.py` | GPT generator CLI | Generate Logic App expressions |

### Training Notebooks

| Notebook | Purpose | See Documentation |
|----------|---------|-------------------|
| `notebooks/az_lgc_exp_catagory_bert.ipynb` | Train BERT classifier | [MODEL_TRAINING.md](MODEL_TRAINING.md) |
| `notebooks/az_lgc_exp_gpt2.ipynb` | Train GPT-2 generator | [MODEL_TRAINING.md](MODEL_TRAINING.md) |

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
| `docs/GETTING_STARTED.md` | Step-by-step guide for beginners |
| `docs/PROJECT_STRUCTURE.md` | This file - project organization |
| `docs/PAGINATION.md` | Pagination feature for large datasets |
| `docs/CLI_USAGE.md` | Using BERT classifier and GPT generator CLIs |
| `docs/MODEL_TRAINING.md` | Training models with Jupyter notebooks |
| `CHANGELOG.md` | Project changes and version history |

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

### clis/run_bert_model.py

**CLI Tool for BERT Classifier**

**Key Classes:**
- `BERTClassifierCLI` - Interactive REPL for classification

**Key Methods:**
- `classify()` - Classify if text is Azure Logic App expression
- `repl()` - Interactive REPL mode

**Dependencies:**
- transformers - HuggingFace models
- torch - PyTorch framework

**See:** [CLI_USAGE.md](CLI_USAGE.md) for complete documentation

### clis/run_gpt_model.py

**CLI Tool for GPT-2 Generator**

**Key Classes:**
- `GPTModelCLI` - Interactive REPL for generation

**Key Methods:**
- `generate()` - Generate Logic App expression from prompt
- `repl()` - Interactive REPL mode

**Dependencies:**
- transformers - HuggingFace models
- torch - PyTorch framework

**See:** [CLI_USAGE.md](CLI_USAGE.md) for complete documentation

## Trained Models

### models/bert_classifier_azlgcexp_base/

**BERT Binary Classifier**

- **Purpose**: Classify if text is an Azure Logic App expression
- **Base Model**: `bert-base-uncased` (110M parameters)
- **Training**: Fine-tuned on categorization dataset
- **Accuracy**: ~95-98% on test set
- **Files**:
  - `config.json` - Model configuration
  - `model.safetensors` - Model weights
  - `tokenizer_config.json`, `vocab.txt` - Tokenizer files
  - `README.md` - Model card

**HuggingFace**: `albertleigh/azlgc-bert-classifier`

### models/azLgcExpGpt_HF/

**GPT-2 Expression Generator**

- **Purpose**: Generate Azure Logic App expressions from natural language
- **Base Model**: `gpt2` (124M parameters)
- **Training**: Fine-tuned on question-answer pairs
- **Format**: `QUESTION: [nl] ANSWER: [expression]`
- **Files**:
  - `config.json` - Model configuration
  - `model.safetensors` - Model weights
  - `tokenizer_config.json`, `vocab.json`, `merges.txt` - Tokenizer files
  - `generation_config.json` - Generation parameters

**HuggingFace**: `albertleigh/azlgc-gpt`

**See:** [MODEL_TRAINING.md](MODEL_TRAINING.md) for training details

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

### Core Scraping
```
requests>=2.31.0        # HTTP client
PyGithub>=2.1.1         # GitHub API
beautifulsoup4>=4.12.0  # HTML parsing (if needed)
python-dotenv>=1.0.0    # Environment variables
pandas>=2.1.0           # Data manipulation
tqdm>=4.66.0            # Progress bars
```

### CLI Tools (requirements-clis.txt)
```
transformers>=4.30.0    # HuggingFace models
torch>=2.0.0            # PyTorch
```

### Training Notebooks
```
datasets                # HuggingFace datasets
transformers            # Model architectures
torch                   # Deep learning framework
matplotlib              # Visualization
numpy                   # Numerical computing
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

### Data Collection & Scraping

```bash
# Run demo (no GitHub token required)
python demo.py

# Scrape small dataset
python scrape_logic_apps.py --max-files 20

# Scrape large dataset with patterns
python scrape_logic_apps.py --max-files 2000 --patterns "concat(" "variables("

# Run tests
pytest tests/ -v
```

### Model Training

```bash
# Open BERT training notebook
code notebooks/az_lgc_exp_catagory_bert.ipynb

# Open GPT-2 training notebook
code notebooks/az_lgc_exp_gpt2.ipynb

# See: docs/MODEL_TRAINING.md for detailed guide
```

### Using Trained Models

```bash
# BERT Classifier (Interactive)
python clis/run_bert_model.py

# BERT Classifier (Single query)
python clis/run_bert_model.py -t "@{variables('myVar')}"

# GPT Generator (Interactive)
python clis/run_gpt_model.py

# GPT Generator (Single query)
python clis/run_gpt_model.py -p "QUESTION: Get the trigger body."

# See: docs/CLI_USAGE.md for complete CLI documentation
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
