# Azure Logic App Expression Tools

Toolkit for Azure Logic App expressions: trained models (BERT classifier & GPT-2 generator) + GitHub scraper for building training datasets.

## Quick Start: Using the Trained Models

### GPT Expression Generator

Generate Logic App expressions from natural language:

```bash
python clis/run_gpt_model.py
```

**Example Session**:
```
Loading model... ✓

============================================================
AzLgcExp Interactive CLI
============================================================

> QUESTION: Get the value of the variable ContributionsAdded.

QUESTION: Get the value of the variable ContributionsAdded. ANSWER: @variables('ContributionsAdded').

> QUESTION: Get the Name property from the first item in the FilterContributionTypes action's output.

QUESTION: Get the Name property from the first item in the FilterContributionTypes action's output. 
ANSWER: @{first(filterContributionTypes('Name')?['properties']?['Name'])}.
```

### BERT Expression Classifier

Classify whether text is an Azure Logic App expression:

```bash
python clis/run_bert_model.py
```

**Example Session**:
```
Loading model... ✓

============================================================
AzLgcExp BERT Classifier - Interactive CLI
============================================================

> @{body('Parse_JSON')?['content']?['main_text']}

============================================================
Result: Azure Logic App Expression
============================================================
Non-Azure Logic App: 0.0006 (0.06%)
Azure Logic App:     0.9994 (99.94%)

> tokenizer(text, return_tensors='pt')

============================================================
Result: Non-Azure Logic App Expression
============================================================
Non-Azure Logic App: 0.9831 (98.31%)
Azure Logic App:     0.0169 (1.69%)
```

**Models**: Available on HuggingFace
- [`albertleigh/azlgc-gpt`](https://huggingface.co/albertleigh/azlgc-gpt) - GPT-2 generator
- [`albertleigh/azlgc-bert-classifier`](https://huggingface.co/albertleigh/azlgc-bert-classifier) - BERT classifier

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-clis.txt
```

## Dataset Collection (Optional)

Scrape GitHub to build your own training datasets.

**Pre-built Dataset**: [`albertleigh/az-logic-apps-dataset`](https://huggingface.co/datasets/albertleigh/az-logic-apps-dataset) on HuggingFace

```bash
# Quick demo (no GitHub token needed)
python demo.py

# Scrape Logic App workflows from GitHub
python scrape_logic_apps.py --max-files 100 --patterns "concat(" "variables("
```

**Setup GitHub Token** (for better rate limits):
```bash
# Create .env file
echo "GITHUB_TOKEN=your_github_token_here" > .env
```

**Output**: Creates training datasets in `datasets/` directory (JSONL, JSON, CSV formats)

## Documentation

| Guide | Description |
|-------|-------------|
| **[CLI Usage](docs/CLI_USAGE.md)** | Using BERT classifier and GPT-2 generator CLIs |
| **[Model Training](docs/MODEL_TRAINING.md)** | Training models with Jupyter notebooks |
| **[Getting Started](docs/GETTING_STARTED.md)** | Beginner's guide to data collection |
| **[Pagination](docs/PAGINATION.md)** | Collecting large datasets (>1000 files) |
| **[Project Structure](docs/PROJECT_STRUCTURE.md)** | Project organization and architecture |

## Project Structure

```
az-lgc-finetuned/
├── clis/                       # CLI tools for trained models
│   ├── run_bert_model.py       # BERT classifier
│   └── run_gpt_model.py        # GPT-2 generator
├── models/                     # Trained models (local)
│   ├── bert_classifier_azlgcexp_base/
│   └── azLgcExpGpt_HF/
├── notebooks/                  # Training notebooks
│   ├── az_lgc_exp_catagory_bert.ipynb
│   └── az_lgc_exp_gpt2.ipynb
├── scrapers/                   # GitHub scraping & parsing
│   ├── github_scraper.py
│   ├── expression_parser.py
│   └── dataset_builder.py
├── docs/                       # Documentation
└── datasets/                   # Generated datasets (output)
```

## License

This project is for educational and research purposes. Respect GitHub's terms of service and API usage guidelines.
