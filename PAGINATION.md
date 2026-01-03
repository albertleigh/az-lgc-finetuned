# Pagination Support for Large Datasets

## Overview

GitHub's code search API has a hard limit of **1000 results per query**. To collect larger datasets, this scraper includes a pagination strategy that automatically splits queries into multiple sub-queries.

## How It Works

The pagination strategy splits queries by **star ranges**:
- 0-10 stars
- 10-50 stars  
- 50-100 stars
- 100-500 stars
- 500-1000 stars
- 1000-5000 stars
- 5000+ stars

Each sub-query can return up to 1000 results, allowing you to collect thousands of files.

## Usage

### Command Line

```bash
# Collect up to 2000 files (uses pagination automatically)
python scrape_logic_apps.py --max-files 2000

# Collect up to 5000 files with minimum stars filter
python scrape_logic_apps.py --max-files 5000 --min-stars 5

# Disable pagination (limit to 1000 results)
python scrape_logic_apps.py --max-files 2000 --no-pagination
```

### Python API

```python
from scrapers import DatasetBuilder

builder = DatasetBuilder()
builder.initialize_scraper()

# Scrape up to 3000 files (pagination enabled by default)
builder.scrape_workflows(
    max_files=3000,
    min_stars=10,
    use_pagination=True
)
```

### Direct Scraper Usage

```python
from scrapers import GitHubLogicAppScraper

scraper = GitHubLogicAppScraper()

# Search with pagination (can exceed 1000)
files = scraper.search_logic_app_files(
    max_results=2500,
    min_stars=5,
    use_pagination_strategy=True
)

# Without pagination (max 1000)
files = scraper.search_logic_app_files(
    max_results=500,
    use_pagination_strategy=False
)

# Pattern-based search with pagination
files = scraper.search_by_expression_patterns(
    patterns=['concat(', 'variables(', 'parameters('],
    max_results=2000,
    use_pagination_strategy=True
)
```

## Examples

### Example 1: Small Dataset (No Pagination Needed)
```bash
# 500 files - no pagination needed
python scrape_logic_apps.py --max-files 500 --min-stars 10
```

### Example 2: Medium Dataset (Auto Pagination)
```bash
# 2000 files - automatically uses pagination
python scrape_logic_apps.py --max-files 2000 --min-stars 5
```

### Example 3: Large Dataset (High Quality)
```bash
# 5000 files from popular repos
python scrape_logic_apps.py --max-files 5000 --min-stars 50
```

### Example 4: Maximum Dataset
```bash
# Collect as many as possible (will take time!)
python scrape_logic_apps.py --max-files 10000 --min-stars 0
```

## Performance Considerations

### Rate Limits
With authentication:
- **Search API**: 30 requests/minute
- **Core API**: 5000 requests/hour

Each star-range query counts as 1 search request. For 2000 files across 8 star ranges, expect ~8 search API calls.

### Timing
- 100 files: ~30 seconds
- 1000 files: ~5 minutes
- 2000 files: ~10-15 minutes  
- 5000 files: ~30-45 minutes
- 10000 files: ~1-2 hours

### Tips for Large Datasets

1. **Use a GitHub token** - Required for reasonable rate limits
2. **Start small** - Test with 100-200 files first
3. **Use min_stars** - Filter by popular repos for better quality
4. **Be patient** - Large collections take time due to rate limits
5. **Monitor progress** - Watch the progress bars and logs

## How Deduplication Works

When using pagination, files may appear in multiple star-range queries. The scraper automatically deduplicates based on file URL, so you won't get duplicate files even if they match multiple ranges.

## Limitations

- Maximum practical limit: ~7000-8000 unique Logic App files (based on current GitHub availability)
- Each query still limited to 1000 results, pagination splits queries
- Rate limits still apply - plan for longer run times
- Some overlap between star ranges is expected and handled

## Troubleshooting

### "Only got 1000 results even with --max-files 2000"

This means:
- All results fit in one star range (e.g., all repos have <10 stars)
- Try lowering `--min-stars` or adjusting query

### "Rate limit exceeded"

- Wait for rate limit to reset
- Check limits: `python -c "from scrapers import GitHubLogicAppScraper; s = GitHubLogicAppScraper(); print(s.get_rate_limit_info())"`
- Add delays between runs

### "Taking too long"

- Reduce `--max-files`
- Increase `--min-stars` to filter to fewer, higher-quality repos
- Use `--patterns` to narrow search scope

## API Reference

### search_logic_app_files

```python
def search_logic_app_files(
    self,
    query: str = '"Microsoft.Logic/workflows" OR "$schema" logic language:JSON',
    max_results: int = 100,
    min_stars: int = 0,
    use_pagination_strategy: bool = True
) -> List[Dict]:
    """
    Search GitHub for Logic App workflow files.
    
    Args:
        query: GitHub code search query
        max_results: Maximum files to retrieve (can exceed 1000)
        min_stars: Minimum repository stars
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
