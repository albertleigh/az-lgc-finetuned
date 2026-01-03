"""
Dataset builder for creating fine-tuning datasets from scraped Logic App expressions.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from tqdm import tqdm

from .github_scraper import GitHubLogicAppScraper, load_results, save_results
from .expression_parser import LogicAppExpressionParser


class DatasetBuilder:
    """Build training datasets from scraped Logic App workflows."""
    
    def __init__(self, output_dir: str = "datasets"):
        """
        Initialize dataset builder.
        
        Args:
            output_dir: Directory to save datasets
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.scraper = None
        self.parser = LogicAppExpressionParser()
        
        self.raw_files = []
        self.processed_workflows = []
        self.expressions = []
        self.training_samples = []
    
    def initialize_scraper(self, token: Optional[str] = None):
        """Initialize GitHub scraper with token."""
        self.scraper = GitHubLogicAppScraper(token)
    
    def scrape_workflows(self, 
                        max_files: int = 100,
                        min_stars: int = 0,
                        search_patterns: Optional[List[str]] = None) -> int:
        """
        Scrape Logic App workflows from GitHub.
        
        Args:
            max_files: Maximum number of files to scrape
            min_stars: Minimum repository stars
            search_patterns: Optional list of patterns to search for
            
        Returns:
            Number of files scraped
        """
        if not self.scraper:
            raise ValueError("Scraper not initialized. Call initialize_scraper() first.")
        
        print("\n=== Scraping Logic App Workflows ===")
        
        # Search for workflow files
        if search_patterns:
            files = self.scraper.search_by_expression_patterns(
                search_patterns,
                max_results=max_files
            )
        else:
            files = self.scraper.search_logic_app_files(
                max_results=max_files,
                min_stars=min_stars
            )
        
        self.raw_files = files
        
        # Save raw file list
        save_results(files, self.output_dir / "raw_files.json")
        
        return len(files)
    
    def download_and_parse_workflows(self, files: Optional[List[Dict]] = None) -> int:
        """
        Download workflow content and parse expressions.
        
        Args:
            files: Optional list of file info dicts (uses self.raw_files if not provided)
            
        Returns:
            Number of workflows processed
        """
        if not self.scraper:
            raise ValueError("Scraper not initialized. Call initialize_scraper() first.")
        
        files = files or self.raw_files
        if not files:
            print("No files to process.")
            return 0
        
        print(f"\n=== Processing {len(files)} Workflow Files ===")
        
        processed_count = 0
        
        for file_info in tqdm(files, desc="Processing workflows"):
            # Download content
            content = self.scraper.download_file_content(file_info)
            if not content:
                continue
            
            # Check if it's a Logic App workflow
            if not self.parser.is_logic_app_workflow(content):
                continue
            
            # Parse workflow
            workflow = self.parser.parse_workflow(content)
            if not workflow:
                continue
            
            # Extract expressions
            expressions = self.parser.extract_all_expressions(workflow)
            
            if expressions:
                workflow_data = {
                    'file_info': file_info,
                    'workflow': workflow,
                    'expressions': expressions,
                    'expression_count': len(expressions),
                    'statistics': self.parser.get_expression_statistics(expressions),
                    'processed_at': datetime.now().isoformat()
                }
                
                self.processed_workflows.append(workflow_data)
                self.expressions.extend(expressions)
                processed_count += 1
        
        # Save processed workflows
        save_results(self.processed_workflows, self.output_dir / "processed_workflows.json")
        
        print(f"\nProcessed {processed_count} workflows with {len(self.expressions)} total expressions")
        
        return processed_count
    
    def create_training_dataset(self, 
                                min_quality_score: float = 0.0,
                                deduplicate: bool = True) -> int:
        """
        Create training dataset from extracted expressions.
        
        Args:
            min_quality_score: Minimum quality score for samples (0-1)
            deduplicate: Remove duplicate expressions
            
        Returns:
            Number of training samples created
        """
        print(f"\n=== Creating Training Dataset ===")
        
        training_samples = []
        seen_expressions = set()
        
        for workflow_data in tqdm(self.processed_workflows, desc="Creating samples"):
            file_info = workflow_data['file_info']
            
            for expression in workflow_data['expressions']:
                expr_text = expression['raw_expression']
                
                # Skip duplicates if requested
                if deduplicate and expr_text in seen_expressions:
                    continue
                
                # Create training sample
                sample = self.parser.create_training_sample(
                    expression,
                    workflow_context=workflow_data['workflow']
                )
                
                # Add metadata
                sample['metadata'] = {
                    'source_repo': file_info['repo_name'],
                    'source_file': file_info['file_path'],
                    'source_url': file_info['url'],
                    'repo_stars': file_info.get('repo_stars', 0),
                }
                
                # Calculate simple quality score
                quality_score = self._calculate_quality_score(expression, file_info)
                sample['quality_score'] = quality_score
                
                if quality_score >= min_quality_score:
                    training_samples.append(sample)
                    seen_expressions.add(expr_text)
        
        self.training_samples = training_samples
        
        # Save in multiple formats
        self._save_training_dataset()
        
        print(f"\nCreated {len(training_samples)} training samples")
        
        return len(training_samples)
    
    def _calculate_quality_score(self, expression: Dict, file_info: Dict) -> float:
        """
        Calculate a quality score for an expression.
        
        Args:
            expression: Expression dictionary
            file_info: File information dictionary
            
        Returns:
            Quality score between 0 and 1
        """
        score = 0.5  # Base score
        
        # Boost for repository popularity
        stars = file_info.get('repo_stars', 0)
        if stars > 100:
            score += 0.2
        elif stars > 10:
            score += 0.1
        
        # Boost for complexity (but not too complex)
        func_count = expression['function_count']
        if 1 <= func_count <= 5:
            score += 0.2
        elif func_count > 5:
            score += 0.1
        
        # Boost for common patterns
        if expression['has_variables'] or expression['has_parameters']:
            score += 0.1
        
        return min(score, 1.0)
    
    def _save_training_dataset(self):
        """Save training dataset in multiple formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON format (full data)
        json_path = self.output_dir / f"training_dataset_{timestamp}.json"
        save_results(self.training_samples, json_path)
        
        # JSONL format (for fine-tuning)
        jsonl_path = self.output_dir / f"training_dataset_{timestamp}.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for sample in self.training_samples:
                # Format for instruction fine-tuning
                training_entry = {
                    'prompt': f"Translate this natural language to Azure Logic App expression: {sample['natural_language']}",
                    'completion': sample['expression']
                }
                f.write(json.dumps(training_entry, ensure_ascii=False) + '\n')
        
        print(f"Saved JSONL format: {jsonl_path}")
        
        # CSV format (for analysis)
        csv_path = self.output_dir / f"training_dataset_{timestamp}.csv"
        df = pd.DataFrame([
            {
                'natural_language': s['natural_language'],
                'expression': s['expression'],
                'functions': ','.join(s['functions']),
                'context': s['context'],
                'nesting_level': s['complexity']['nesting_level'],
                'function_count': s['complexity']['function_count'],
                'quality_score': s['quality_score'],
                'source_repo': s['metadata']['source_repo'],
                'repo_stars': s['metadata']['repo_stars']
            }
            for s in self.training_samples
        ])
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"Saved CSV format: {csv_path}")
    
    def generate_statistics_report(self) -> Dict:
        """Generate statistics report about the dataset."""
        if not self.training_samples:
            return {'error': 'No training samples available'}
        
        df = pd.DataFrame([
            {
                'expression': s['expression'],
                'function_count': s['complexity']['function_count'],
                'nesting_level': s['complexity']['nesting_level'],
                'quality_score': s['quality_score'],
                'repo_stars': s['metadata']['repo_stars']
            }
            for s in self.training_samples
        ])
        
        report = {
            'total_samples': len(self.training_samples),
            'total_workflows': len(self.processed_workflows),
            'unique_expressions': df['expression'].nunique(),
            'avg_function_count': float(df['function_count'].mean()),
            'avg_nesting_level': float(df['nesting_level'].mean()),
            'avg_quality_score': float(df['quality_score'].mean()),
            'function_count_distribution': df['function_count'].value_counts().to_dict(),
            'top_repositories': df.groupby('repo_stars').size().sort_values(ascending=False).head(10).to_dict()
        }
        
        # Save report
        report_path = self.output_dir / "dataset_statistics.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nDataset Statistics:")
        print(f"  Total samples: {report['total_samples']}")
        print(f"  Unique expressions: {report['unique_expressions']}")
        print(f"  Avg functions per expression: {report['avg_function_count']:.2f}")
        print(f"  Avg quality score: {report['avg_quality_score']:.2f}")
        
        return report
    
    def load_existing_data(self, files_path: str, workflows_path: Optional[str] = None):
        """
        Load previously scraped data.
        
        Args:
            files_path: Path to raw_files.json
            workflows_path: Optional path to processed_workflows.json
        """
        self.raw_files = load_results(files_path)
        print(f"Loaded {len(self.raw_files)} file records")
        
        if workflows_path:
            self.processed_workflows = load_results(workflows_path)
            print(f"Loaded {len(self.processed_workflows)} processed workflows")
            
            # Extract expressions
            self.expressions = []
            for workflow_data in self.processed_workflows:
                self.expressions.extend(workflow_data['expressions'])
