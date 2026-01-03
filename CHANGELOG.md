# Changelog

## 2026-01-04 - Bug Fixes & Improvements

### Fixed: AttributeError with list-formatted triggers/actions

**Issue**: Some Logic App workflows from GitHub have `triggers` and `actions` defined as lists instead of dictionaries, causing `AttributeError: 'list' object has no attribute 'items'`

**Solution**: 
- Updated `expression_parser.py` to handle both dict and list formats for triggers/actions
- Added try-except wrapper in `dataset_builder.py` to gracefully skip malformed files
- Added test case `test_workflow_with_list_format` to verify the fix

### Improved: GitHub search query and ARM template support

**Issue**: Default search query `filename:workflow.json` was too generic and returned non-Azure workflows (n8n, ComfyUI, etc.). Only 0 out of 30 files were actual Logic Apps.

**Solution**:
- Changed default search query to `"Microsoft.Logic/workflows" OR "$schema" logic language:JSON`
- Added ARM template detection and parsing (Logic Apps embedded in Azure Resource Manager templates)
- Improved workflow detection to be more strict about what qualifies as a Logic App
- Added diagnostic counters for skipped files (not workflow, no expressions, errors)

**Files Changed**:
- `scrapers/github_scraper.py` - Better default search query
- `scrapers/expression_parser.py` - ARM template support, stricter detection
- `scrapers/dataset_builder.py` - Better error reporting with skip counters

**Testing**: All 12 tests passing ✅ + ARM template test successful (32 expressions extracted)

### Usage

The improved search will automatically target Azure Logic Apps:
```bash
python scrape_logic_apps.py --max-files 100 --min-stars 5
```

Or use custom patterns:
```bash
python scrape_logic_apps.py --patterns "concat" "variables" "triggerBody"
```
