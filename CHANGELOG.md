# Changelog

## 2026-01-04 - Pagination Support for Pattern-Based Searches

### Enhancement: search_by_expression_patterns now supports pagination ✨

**Feature**: Extended pagination support to pattern-based searches (`--patterns` flag).

**Previous limitation**: Pattern searches were limited to 1000 results even with `max_files > 1000`.

**New behavior**:
- `search_by_expression_patterns()` now accepts `use_pagination_strategy` parameter
- Uses same star-range splitting strategy as `search_logic_app_files()`
- Automatically enabled when searching with patterns and `max_files > 1000`
- Works with CLI `--no-pagination` flag

**Example**:
```bash
# Pattern search with pagination (can exceed 1000)
python scrape_logic_apps.py --max-files 2000 --patterns "concat(" "variables("

# Without pagination (limit 1000)
python scrape_logic_apps.py --max-files 2000 --patterns "concat(" --no-pagination
```

**Files Changed**:
- `scrapers/github_scraper.py`:
  - Added `use_pagination_strategy` parameter to `search_by_expression_patterns()`
  - Added `_search_pattern_single()` for single query execution
  - Added `_search_pattern_with_pagination()` for paginated pattern searches
- `scrapers/dataset_builder.py`:
  - Updated `scrape_workflows()` to pass `use_pagination` to pattern searches
- `PAGINATION.md` - Added pattern-based search examples

**Test Results**:
- Without pagination: 46 files, 128 training samples (3 patterns)
- With pagination: 88 files, 578 training samples (3 patterns)
- **4.5x more samples** with pagination enabled! 🚀

---

## 2026-01-04 - Pagination Support for Large Datasets

### New Feature: Pagination Strategy to Exceed 1000 Result Limit ✨

**Feature**: Added pagination support to collect more than 1000 files (GitHub's per-query limit).

**How it works**:
- Automatically splits queries by star ranges (0-10, 10-50, 50-100, etc.)
- Each sub-query can return up to 1000 results
- Deduplicates results across ranges
- Enabled by default when `max_files > 1000`

**Usage**:
```bash
# Collect up to 5000 files (uses pagination)
python scrape_logic_apps.py --max-files 5000

# Disable pagination if needed
python scrape_logic_apps.py --max-files 2000 --no-pagination
```

**Files Changed**:
- `scrapers/github_scraper.py` - Added `_search_with_pagination_strategy()` method
- `scrapers/dataset_builder.py` - Added `use_pagination` parameter
- `scrape_logic_apps.py` - Added `--no-pagination` CLI option
- `PAGINATION.md` - New documentation for pagination feature

**Benefits**:
- ✅ Collect datasets larger than 1000 samples
- ✅ Automatic deduplication
- ✅ Rate limit aware with delays between queries
- ✅ Progress tracking for each star range

See [PAGINATION.md](PAGINATION.md) for detailed documentation.

---

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
