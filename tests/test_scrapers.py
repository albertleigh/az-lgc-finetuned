"""
Test suite for Logic App expression scrapers and parsers.
"""

import pytest
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.expression_parser import LogicAppExpressionParser
from scrapers.github_scraper import GitHubLogicAppScraper


class TestLogicAppExpressionParser:
    """Test cases for expression parser."""
    
    @pytest.fixture
    def parser(self):
        return LogicAppExpressionParser()
    
    def test_simple_expression_extraction(self, parser):
        """Test extracting a simple expression."""
        expression = "@{concat('Hello', ' ', 'World')}"
        result = parser.analyze_expression(expression)
        
        assert result['raw_expression'] == expression
        assert 'concat' in result['functions_used']
        assert result['function_count'] == 1
    
    def test_nested_expression(self, parser):
        """Test extracting nested expressions."""
        expression = "@{concat(variables('firstName'), ' ', variables('lastName'))}"
        result = parser.analyze_expression(expression)
        
        assert 'concat' in result['functions_used']
        assert 'variables' in result['functions_used']
        assert result['function_count'] == 3  # concat + 2 variables
        assert result['has_variables'] is True
    
    def test_workflow_detection(self, parser):
        """Test Logic App workflow detection."""
        valid_workflow = json.dumps({
            "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
            "actions": {},
            "triggers": {}
        })
        
        assert parser.is_logic_app_workflow(valid_workflow) is True
        
        invalid_workflow = json.dumps({"random": "data"})
        assert parser.is_logic_app_workflow(invalid_workflow) is False
    
    def test_extract_from_workflow(self, parser):
        """Test extracting expressions from a complete workflow."""
        workflow = {
            "definition": {
                "actions": {
                    "SendEmail": {
                        "inputs": {
                            "body": "@{concat('Hello ', variables('userName'))}",
                            "subject": "Greeting"
                        }
                    }
                }
            }
        }
        
        expressions = parser.extract_all_expressions(workflow)
        assert len(expressions) > 0
        assert any('concat' in e['functions_used'] for e in expressions)
    
    def test_expression_statistics(self, parser):
        """Test statistics generation."""
        expressions = [
            parser.analyze_expression("@{concat('a', 'b')}"),
            parser.analyze_expression("@{variables('x')}"),
            parser.analyze_expression("@{concat('a', 'b')}")  # duplicate
        ]
        
        stats = parser.get_expression_statistics(expressions)
        assert stats['total_expressions'] == 3
        assert stats['unique_expressions'] == 2
        assert 'concat' in stats['function_usage']
    
    def test_training_sample_creation(self, parser):
        """Test creating training samples."""
        expression = {
            'raw_expression': "@{concat('Hello', variables('name'))}",
            'functions_used': ['concat', 'variables'],
            'function_count': 2,
            'nesting_level': 1,
            'has_variables': True,
            'context': 'actions.SendEmail.inputs.body'
        }
        
        sample = parser.create_training_sample(expression)
        assert 'natural_language' in sample
        assert 'expression' in sample
        assert sample['expression'] == expression['raw_expression']
    
    def test_complex_expression(self, parser):
        """Test parsing complex nested expression."""
        complex_expr = "@{if(equals(variables('status'), 'active'), concat('User ', variables('name'), ' is active'), 'User is inactive')}"
        result = parser.analyze_expression(complex_expr)
        
        assert 'if' in result['functions_used']
        assert 'equals' in result['functions_used']
        assert 'concat' in result['functions_used']
        assert 'variables' in result['functions_used']
        assert result['nesting_level'] > 1
    
    def test_workflow_with_list_format(self, parser):
        """Test extracting expressions from workflow with triggers/actions as lists."""
        workflow = {
            "definition": {
                "triggers": [
                    {
                        "type": "Request",
                        "inputs": {
                            "body": "@{triggerBody()}"
                        }
                    }
                ],
                "actions": [
                    {
                        "type": "Compose",
                        "inputs": "@{concat('Hello', variables('name'))}"
                    }
                ]
            }
        }
        
        expressions = parser.extract_all_expressions(workflow)
        assert len(expressions) >= 2
        assert any('triggerBody' in e['functions_used'] for e in expressions)
        assert any('concat' in e['functions_used'] for e in expressions)


class TestGitHubScraper:
    """Test cases for GitHub scraper."""
    
    @pytest.fixture
    def scraper(self):
        # Don't use token for tests to avoid rate limit issues
        return GitHubLogicAppScraper(token=None)
    
    def test_scraper_initialization(self, scraper):
        """Test scraper initializes correctly."""
        assert scraper is not None
        assert scraper.github is not None
    
    def test_rate_limit_info(self, scraper):
        """Test getting rate limit information."""
        try:
            rate_info = scraper.get_rate_limit_info()
            assert 'core_limit' in rate_info or 'error' in rate_info
        except Exception as e:
            # Rate limit check might fail without token
            pytest.skip(f"Rate limit check requires authentication: {e}")
    
    @pytest.mark.slow
    def test_search_logic_app_files(self, scraper):
        """Test searching for Logic App files (slow test)."""
        try:
            files = scraper.search_logic_app_files(max_results=2)
            # Should return results or empty list (not error)
            assert isinstance(files, list)
        except Exception as e:
            pytest.skip(f"Search requires network and may hit rate limits: {e}")


class TestIntegration:
    """Integration tests combining scraper and parser."""
    
    def test_sample_workflow_parsing(self):
        """Test parsing a sample workflow end-to-end."""
        parser = LogicAppExpressionParser()
        
        sample_workflow = {
            "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
            "contentVersion": "1.0.0.0",
            "definition": {
                "triggers": {
                    "manual": {
                        "type": "Request",
                        "kind": "Http"
                    }
                },
                "actions": {
                    "Initialize_variable": {
                        "type": "InitializeVariable",
                        "inputs": {
                            "variables": [{
                                "name": "userName",
                                "type": "string",
                                "value": "@{triggerBody()?['name']}"
                            }]
                        }
                    },
                    "Compose_message": {
                        "type": "Compose",
                        "inputs": "@{concat('Hello, ', variables('userName'), '!')}",
                        "runAfter": {
                            "Initialize_variable": ["Succeeded"]
                        }
                    }
                }
            }
        }
        
        # Parse workflow
        expressions = parser.extract_all_expressions(sample_workflow)
        
        # Should find expressions
        assert len(expressions) > 0
        
        # Should find specific functions
        all_functions = []
        for expr in expressions:
            all_functions.extend(expr['functions_used'])
        
        assert 'triggerBody' in all_functions or 'concat' in all_functions or 'variables' in all_functions
        
        # Create training samples
        samples = [parser.create_training_sample(e) for e in expressions]
        assert len(samples) == len(expressions)
        
        for sample in samples:
            assert 'natural_language' in sample
            assert 'expression' in sample
            assert sample['expression'].startswith('@')


def test_expression_patterns():
    """Test various expression patterns."""
    parser = LogicAppExpressionParser()
    
    test_cases = [
        # Simple function call
        ("@{concat('a', 'b')}", ['concat']),
        # Variables
        ("@{variables('myVar')}", ['variables']),
        # Parameters
        ("@{parameters('myParam')}", ['parameters']),
        # Trigger body
        ("@{triggerBody()}", ['triggerBody']),
        # Action output
        ("@{body('myAction')}", ['body']),
        # Nested functions
        ("@{concat(variables('x'), variables('y'))}", ['concat', 'variables']),
        # Conditional
        ("@{if(equals(1, 1), 'true', 'false')}", ['if', 'equals']),
        # String manipulation
        ("@{substring(variables('text'), 0, 5)}", ['substring', 'variables']),
        # Date/time
        ("@{formatDateTime(utcNow(), 'yyyy-MM-dd')}", ['formatDateTime', 'utcNow']),
    ]
    
    for expression, expected_functions in test_cases:
        result = parser.analyze_expression(expression)
        for func in expected_functions:
            assert func in result['functions_used'], f"Expected {func} in {expression}"


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '-s'])
