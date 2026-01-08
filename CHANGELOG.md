# Changelog

## 2026-01-08 - Project Documentation & Model Release

### Added

**Trained Models & CLI Tools**
- BERT classifier (`albertleigh/azlgc-bert-classifier`) - 95-98% accuracy for identifying Logic App expressions
- GPT-2 generator (`albertleigh/azlgc-gpt`) - Generates Logic App expressions from natural language
- Interactive CLI tools: `run_bert_model.py` and `run_gpt_model.py`
- Training notebooks: `az_lgc_exp_catagory_bert.ipynb` and `az_lgc_exp_gpt2.ipynb`

**Documentation**
- [CLI_USAGE.md](docs/CLI_USAGE.md) - Complete guide for using trained models
- [MODEL_TRAINING.md](docs/MODEL_TRAINING.md) - Notebook training guide with tips and troubleshooting
- [PAGINATION.md](docs/PAGINATION.md) - Merged and updated pagination documentation
- [GETTING_STARTED.md](docs/GETTING_STARTED.md) - Updated to reflect current implementation
- [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) - Added model and CLI documentation

**Dataset**
- Published dataset: `albertleigh/az-logic-apps-dataset` on HuggingFace

### Changed

**GitHub Scraping**
- Implements page-based pagination (30 results per page)
- Pattern-based search for exceeding 1000-result limit
- Auto-applies default patterns when `--max-files > 1000`
- Improved search query: `"Microsoft.Logic/workflows" OR "$schema" logic`
- ARM template support for embedded Logic App workflows

**Documentation Structure**
- Consolidated pagination docs (removed `BEFORE_AFTER_PAGINATION.md`, `PAGINATION_PATTERNS_IMPLEMENTATION.md`)
- Simplified README.md with focus on CLI usage
- Added HuggingFace links for models and dataset

### Technical Details

**Pagination Implementation**:
- Uses GitHub's `get_page()` method for page-based pagination
- Each query returns up to ~1000 results
- Multiple patterns = multiple queries = can exceed 1000 total files
- Automatic deduplication across patterns

**Models**:
- BERT: `bert-base-uncased` fine-tuned for binary classification (110M parameters)
- GPT-2: `gpt2` fine-tuned for expression generation (124M parameters)
- Both available locally in `models/` and on HuggingFace

See documentation in `docs/` for detailed guides.
