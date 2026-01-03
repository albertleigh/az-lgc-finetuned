"""
GitHub scraper for Azure Logic App expressions.
Searches GitHub for Logic App workflow definitions and extracts expressions.
"""

import os
import json
import time
import re
from typing import List, Dict, Optional, Set
from pathlib import Path
from datetime import datetime

import requests
from github import Github, RateLimitExceededException
from dotenv import load_dotenv
from tqdm import tqdm


class GitHubLogicAppScraper:
    """Scraper for collecting Azure Logic App expressions from GitHub."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the scraper.
        
        Args:
            token: GitHub personal access token (optional, but recommended for higher rate limits)
        """
        load_dotenv()
        self.token = token or os.getenv('GITHUB_TOKEN')
        
        if self.token:
            self.github = Github(self.token)
            self.session = requests.Session()
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        else:
            self.github = Github()
            self.session = requests.Session()
            print("Warning: No GitHub token provided. Rate limits will be restrictive.")
        
        self.rate_limit_wait = 60  # seconds to wait when rate limited
        
    def search_logic_app_files(self, 
                                query: str = '"Microsoft.Logic/workflows" OR "$schema" logic language:JSON',
                                max_results: int = 100) -> List[Dict]:
        """
        Search GitHub for Logic App workflow files with pagination support.
        
        Args:
            query: GitHub code search query
            max_results: Maximum number of files to retrieve
            
        Returns:
            List of file information dictionaries
        """
        return self._search_code_with_pagination(query, max_results)
    
    def _search_code_with_pagination(self, query: str, max_results: int) -> List[Dict]:
        """
        Execute code search with proper GitHub API pagination using get_page().

        Args:
            query: GitHub code search query
            max_results: Maximum number of files to retrieve

        Returns:
            List of file information dictionaries
        """
        files = []
        
        print(f"Searching GitHub with query: {query}")

        try:
            # Search for code files - returns PaginatedList
            results = self.github.search_code(query)
            
            # Check if REST API pagination is supported
            if not results.is_rest:
                print("Warning: REST API pagination not supported, falling back to simple iteration")
                for idx, file in enumerate(results):
                    if len(files) >= max_results:
                        break
                    files.append(self._extract_file_info(file))
                return files
            
            total = min(results.totalCount, max_results)
            print(f"Found {results.totalCount} files (fetching up to {max_results})")
            
            # Use explicit page-based pagination
            page_num = 0
            per_page = 30  # GitHub's default per_page for code search
            
            with tqdm(total=total, desc="Fetching files") as pbar:
                while len(files) < max_results:
                    try:
                        # Get specific page
                        page_results = results.get_page(page_num)
                        
                        # If page is empty, we've reached the end
                        if not page_results:
                            print(f"\nReached end of results at page {page_num}")
                            break
                        
                        # Process files in this page
                        for file in page_results:
                            if len(files) >= max_results:
                                break
                            
                            try:
                                file_info = self._extract_file_info(file)
                                files.append(file_info)
                                pbar.update(1)
                                
                            except Exception as e:
                                print(f"\nError processing file: {e}")
                                continue
                        
                        # Move to next page
                        page_num += 1
                        
                        # # Respect rate limits - sleep between pages
                        # if len(files) < max_results and page_results:
                        #     time.sleep(2)
                            
                    except RateLimitExceededException:
                        print(f"\nRate limit exceeded. Waiting {self.rate_limit_wait} seconds...")
                        time.sleep(self.rate_limit_wait)
                    except Exception as e:
                        print(f"\nError fetching page {page_num}: {e}")
                        break

        except RateLimitExceededException:
            print(f"Rate limit exceeded. Waiting {self.rate_limit_wait} seconds...")
            time.sleep(self.rate_limit_wait)
        except Exception as e:
            print(f"Search error: {e}")

        return files
    
    def _extract_file_info(self, file) -> Dict:
        """
        Extract file information from GitHub API file object.
        
        Args:
            file: GitHub API file object
            
        Returns:
            Dictionary with file information
        """
        return {
            'repo_name': file.repository.full_name,
            'file_path': file.path,
            'file_name': file.name,
            'url': file.html_url,
            'download_url': file.download_url,
            'sha': file.sha,
            'repo_stars': file.repository.stargazers_count,
            'repo_language': file.repository.language,
            'retrieved_at': datetime.now().isoformat()
        }

    def download_file_content(self, file_info: Dict) -> Optional[str]:
        """
        Download the content of a file from GitHub.
        
        Args:
            file_info: Dictionary containing file information
            
        Returns:
            File content as string, or None if download fails
        """
        try:
            response = self.session.get(file_info['download_url'])
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error downloading {file_info['file_path']}: {e}")
            return None
    
    def search_by_expression_patterns(self, 
                                       patterns: List[str],
                                       language: str = 'JSON',
                                       max_results: int = 100) -> List[Dict]:
        """
        Search GitHub for files containing specific Logic App expression patterns.
        
        Args:
            patterns: List of expression patterns to search for (e.g., ['concat', 'variables'])
            language: Programming language filter
            max_results: Total maximum number of results across all patterns
            
        Returns:
            List of file information dictionaries
        """
        all_files = []
        seen_urls = set()
        
        # Calculate results per pattern
        results_per_pattern = max_results // len(patterns) if patterns else max_results
        
        for pattern in patterns:
            if len(all_files) >= max_results:
                break
            
            query = f'{pattern} in:file language:{language} "Microsoft.Logic/workflows" OR "$schema" logic'
            print(f"\n🔍 Searching for pattern: {pattern}")
            
            # Search with pagination
            pattern_results = self._search_pattern_with_pagination(
                pattern, 
                query,
                min(results_per_pattern, max_results - len(all_files))
            )
            
            # Add unique results
            new_count = 0
            for file_info in pattern_results:
                if file_info['url'] not in seen_urls:
                    all_files.append(file_info)
                    seen_urls.add(file_info['url'])
                    new_count += 1
            
            print(f"  Added {new_count} unique files (total: {len(all_files)})")
            
            # Rate limiting between patterns
            if len(all_files) < max_results:
                time.sleep(2)
        
        print(f"\n✅ Total unique files collected: {len(all_files)}")
        return all_files[:max_results]
    
    def _search_pattern_with_pagination(self, pattern: str, query: str, max_results: int) -> List[Dict]:
        """
        Search for a pattern with explicit page-based pagination.
        
        Args:
            pattern: Expression pattern being searched
            query: GitHub code search query
            max_results: Maximum number of results
            
        Returns:
            List of file information dictionaries
        """
        files = []
        
        try:
            results = self.github.search_code(query)
            
            # Check if REST API pagination is supported
            if not results.is_rest:
                print(f"  Warning: REST API pagination not supported for pattern '{pattern}'")
                for idx, file in enumerate(results):
                    if len(files) >= max_results:
                        break
                    file_info = self._extract_file_info(file)
                    file_info['search_pattern'] = pattern
                    files.append(file_info)
                return files
            
            # Use explicit page-based pagination
            page_num = 0
            
            while len(files) < max_results:
                try:
                    # Get specific page
                    page_results = results.get_page(page_num)
                    
                    # If page is empty, we've reached the end
                    if not page_results:
                        break
                    
                    # Process files in this page
                    for file in page_results:
                        if len(files) >= max_results:
                            break
                        
                        try:
                            file_info = self._extract_file_info(file)
                            file_info['search_pattern'] = pattern
                            files.append(file_info)
                            
                        except Exception as e:
                            print(f"  Error processing file: {e}")
                            continue
                    
                    # Move to next page
                    page_num += 1
                    
                    # Respect rate limits - sleep between pages
                    if len(files) < max_results and page_results:
                        time.sleep(2)
                        
                except RateLimitExceededException:
                    print(f"  Rate limit exceeded. Waiting {self.rate_limit_wait} seconds...")
                    time.sleep(self.rate_limit_wait)
                except Exception as e:
                    print(f"  Error fetching page {page_num}: {e}")
                    break
                    
        except RateLimitExceededException:
            print(f"Rate limit exceeded. Waiting {self.rate_limit_wait} seconds...")
            time.sleep(self.rate_limit_wait)
        except Exception as e:
            print(f"Search error for pattern '{pattern}': {e}")
        
        return files
    
    def get_rate_limit_info(self) -> Dict:
        """Get current rate limit information."""
        try:
            rate_limit = self.github.get_rate_limit()
            return {
                'core_limit': rate_limit.core.limit,
                'core_remaining': rate_limit.core.remaining,
                'core_reset': rate_limit.core.reset,
                'search_limit': rate_limit.search.limit,
                'search_remaining': rate_limit.search.remaining,
                'search_reset': rate_limit.search.reset
            }
        except Exception as e:
            return {'error': str(e)}
    
    def search_repositories(self, 
                           keywords: List[str],
                           max_repos: int = 50) -> List[Dict]:
        """
        Search for repositories that likely contain Logic Apps.
        
        Args:
            keywords: Keywords to search for in repository names/descriptions
            max_repos: Maximum number of repositories to return
            
        Returns:
            List of repository information dictionaries
        """
        repos = []
        seen_repos = set()
        
        for keyword in keywords:
            query = f'{keyword} language:JSON'
            print(f"\nSearching repositories with keyword: {keyword}")
            
            try:
                results = self.github.search_repositories(query)
                count = 0
                
                for repo in results:
                    if count >= max_repos:
                        break
                    
                    if repo.full_name in seen_repos:
                        continue
                    
                    try:
                        repo_info = {
                            'full_name': repo.full_name,
                            'description': repo.description,
                            'stars': repo.stargazers_count,
                            'url': repo.html_url,
                            'language': repo.language,
                            'topics': repo.get_topics(),
                            'search_keyword': keyword,
                            'retrieved_at': datetime.now().isoformat()
                        }
                        repos.append(repo_info)
                        seen_repos.add(repo.full_name)
                        count += 1
                        
                    except Exception as e:
                        print(f"Error processing repo: {e}")
                        continue
                
                time.sleep(2)  # Rate limiting
                
            except RateLimitExceededException:
                print(f"Rate limit exceeded. Waiting {self.rate_limit_wait} seconds...")
                time.sleep(self.rate_limit_wait)
            except Exception as e:
                print(f"Search error for keyword '{keyword}': {e}")
        
        return repos


def save_results(data: List[Dict], output_path: str):
    """Save scraping results to a JSON file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(data)} items to {output_path}")


def load_results(input_path: str) -> List[Dict]:
    """Load scraping results from a JSON file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)
