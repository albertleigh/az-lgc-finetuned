# Pagination Support for Large Datasets

## Overview

GitHub's code search API has a hard limit of **1000 results per query**. This scraper uses **page-based pagination** to automatically fetch results across multiple pages, allowing you to collect more than 1000 files when searching for Logic App workflows.

## How It Works

### Page-Based Pagination Strategy

The scraper uses GitHub's REST API pagination to fetch results page by page (30 results per page by default):

1. **Single Query**: Executes one search query per pattern or for general file search
2. **Multi-Page Fetching**: Automatically retrieves subsequent pages until:
   - Desired `max_results` is reached
   - No more results are available
   - GitHub's API limit (1000 results) is hit for that specific query

3. **Pattern-Based Strategy**: When using `--patterns` with multiple patterns:
   - Each pattern executes a separate search query
   - Each query can return up to 1000 results via pagination
   - Results are deduplicated across patterns
   - Example: 3 patterns × 1000 results = up to 3000 unique files

### Key Features

- ✅ **Automatic pagination**: No manual configuration needed
- ✅ **Deduplication**: Files appearing in multiple pattern searches are included only once
- ✅ **Rate limit handling**: Built-in delays between requests
- ✅ **Progress tracking**: Visual progress bars during fetching

## Usage

### Command Line

#### Basic Usage
```bash
# Collect up to 500 files (single query with pagination)
python scrape_logic_apps.py --max-files 500

# Collect more files by using multiple patterns (each pattern = 1 query)
python scrape_logic_apps.py --max-files 2000 --patterns "concat(" "variables(" "parameters("
```

#### Exceeding 1000 Results
When `--max-files > 1000` **without** `--patterns`, the script automatically uses default patterns:
```bash
# Automatically uses 7 default patterns to exceed 1000-result limit
python scrape_logic_apps.py --max-files 2000

# Default patterns used:
# - concat(
# - variables(
# - parameters(
# - triggerBody(
# - json(
# - if(
# - actions(
```

### Python API

#### Basic Scraping
```python
from scrapers import DatasetBuilder

builder = DatasetBuilder()
builder.initialize_scraper()

# Scrape with single query (up to ~1000 files)
builder.scrape_workflows(max_files=500)

# Scrape with patterns to exceed 1000 results
builder.scrape_workflows(
    max_files=3000,
    search_patterns=['concat(', 'variables(', 'parameters(', 'triggerBody(']
)
```

#### Direct Scraper Usage

```python
from scrapers import GitHubLogicAppScraper

scraper = GitHubLogicAppScraper()

# General search with automatic page-based pagination
files = scraper.search_logic_app_files(max_results=500)

# Pattern-based search (each pattern paginated separately)
files = scraper.search_by_expression_patterns(
    patterns=['concat(', 'variables(', 'parameters('],
    max_results=2000  # Distributed across patterns
)
```

## Examples

### Example 1: Small Dataset (< 1000 files)
```bash
# 500 files via single query with page-based pagination
python scrape_logic_apps.py --max-files 500
```

### Example 2: Medium Dataset (1000-3000 files)
```bash
# 2000 files using multiple patterns
python scrape_logic_apps.py --max-files 2000 --patterns "concat(" "variables(" "parameters("
# or let the script auto-select patterns when max-files > 1000
python scrape_logic_apps.py --max-files 2000
```

### Example 3: Large Dataset (3000+ files)
```bash
# 5000 files with multiple patterns (7 patterns × ~700 files each)
python scrape_logic_apps.py --max-files 5000 --patterns "concat(" "variables(" "parameters(" "triggerBody(" "json(" "if(" "actions("
```

### Example 4: Comprehensive Dataset
```bash
# Maximum coverage - automatically uses default patterns
python scrape_logic_apps.py --max-files 10000
```Real-World Performance

### Test Results: Pattern-Based Search

Tested with 3 patterns: `concat(`, `variables(`, `parameters(`

| Approach | Files Found | Training Samples | Improvement |
|----------|-------------|------------------|-------------|
| Single query (no patterns) | 26 files | 128 samples | baseline |
| Multiple patterns (3) | 88 files | 578 samples | **4.5x** |

**Key Takeaway**: Using multiple patterns dramatically increases dataset size and diversity! 🚀

### Rate Limits
With GitHub authentication:
- **Search API**: 30 requests/minute
- **Core API**: 5000 requests/hour

Each pattern search counts as 1 search request. For example:
- 3 patterns = 3 search API calls
- 7 patterns = 7 search API calls

### Timing Estimates
- 100 files (1 pattern): ~30 seconds
- 500 files (1 pattern): ~2-3 minutes
- 1000 files (1 pattern): ~5 minutes
- 2000 files (3 patterns): ~10-15 minutes
- 5000 files (7 patterns): ~30-45 minutes
- 10000 files (7+ patterns): ~1-2 hours

### Tips for Large Datasets

1. **Use a GitHub token** - Required for reasonable rate limits
2. **Start small** - Test with 100-200 files first
3. **Use patterns wisely** - More patterns = more coverage but longer runtime
4. **Be patient** - Large collections take time due to API rate limits
5. **Monitor progress** - Watch the console output for real-time progress

## How Deduplication Works
~1000 results even with --max-files 2000"

**Causes**:
- Single query without patterns hits the 1000-result limit
- Solution: Use `--patterns` flag or let the script auto-select patterns when `max-files > 1000`

**Fix**:
```bash
# Instead of this (limited to ~1000):
python scrape_logic_apps.py --max-files 2000

# Use this (automatically applies default patterns):
python scrape_logic_apps.py --max-files 2000  # Script will auto-apply patterns
# Or explicitly specify patterns:
python scrape_logic_apps.py --max-files 2000 --patterns "concat(" "variables("
```

### "Rate limit exceeded"

**Solution**:
- Wait for rate limit to reset (check reset time in error message)
- Verify your GitHub token is configured in `.env`
- Check current limits:
```bash
python -c "from scrapers import GitHubLogicAppScraper; s = GitHubLogicAppScraper(); print(s.get_rate_limit_info())"
```

### "Taking too long"

**Optimization tips**:
- Reduce `--max-files` for faster results
- Use fewer patterns (e.g., 3 instead of 7)
- Increase `--min-quality` to skip low-quality samples during processing

### "Not enough variety in expressions"

**Solution**: Use more diverse patterns
```bash
python scrape_logic_apps.py --max-files 3000 --patterns "concat(" "variables(" "parameters(" "triggerBody(" "json(" "if(" "substring("
```

## API Reference

### search_logic_app_files

```python
def search_logic_app_files(
    self,
    query: str = '"Microsoft.Logic/workflows" OR "$schema" logic language:JSON',
    max_results: int = 100
) -> List[Dict]:
    """
    Search GitHub for Logic App workflow files with page-based pagination.
    
    Args:
        query: GitHub code search query
        max_results: Maximum files to retrieve (up to ~1000 per query)
    
    Returns:
        List of file information dictionaries
    """
```

### search_by_expression_patterns

```python
def search_by_expression_patterns(
    self,
    patterns: List[str],
    language: str = 'JSON',
    max_results: int = 100
) -> List[Dict]:
    """
    Search for files containing specific Logic App expression patterns.
    Each pattern executes a separate paginated search (up to ~1000 results each).
    Results are automatically deduplicated.
    
    Args:
        patterns: List of patterns to search (e.g., ['concat(', 'variables('])
        language: Programming language filter (default: 'JSON')
        max_results: Total maximum results across all patterns
    
    Returns:
        Deduplicated list of file information dictionaries
    """
```

### Command Line Arguments

```
--max-files INT         Maximum files to scrape (default: 20000)
--patterns [PATTERN...]  Specific patterns to search (e.g., concat( variables()
--min-quality FLOAT     Minimum quality score for training samples (default: 0.0)
--output-dir DIR        Output directory for datasets (default: datasets)
--no-deduplicate        Do not remove duplicate expressions
        use_pagination_strategy: If True and max_results > 1000, 
                                 split query by star ranges
    
    Returns:
        List of file information dictionaries
    """
```

### Command Line Arguments

```
--max-files INT         Maximum files to scrape (default: 100)
--no-pagination        Disable pagination (limits to 1000)
--min-stars INT        Minimum repository stars (default: 5)
```
