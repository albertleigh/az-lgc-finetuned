"""
Parser for extracting and analyzing Azure Logic App expressions.
Handles workflow definition parsing and expression extraction.
"""

import json
import re
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict


class LogicAppExpressionParser:
    """Parser for Azure Logic App workflow definitions and expressions."""
    
    # Common Logic App expression functions
    EXPRESSION_FUNCTIONS = [
        'concat', 'substring', 'replace', 'guid', 'toLower', 'toUpper',
        'trim', 'split', 'join', 'length', 'indexOf', 'lastIndexOf',
        'startsWith', 'endsWith', 'contains',
        'add', 'sub', 'mul', 'div', 'mod', 'min', 'max', 'rand', 'range',
        'string', 'int', 'float', 'bool', 'json', 'xml',
        'variables', 'parameters', 'triggerBody', 'triggerOutputs',
        'actions', 'body', 'outputs', 'result',
        'if', 'equals', 'not', 'and', 'or', 'greater', 'greaterOrEquals',
        'less', 'lessOrEquals', 'empty', 'coalesce',
        'first', 'last', 'take', 'skip', 'intersection', 'union',
        'formatDateTime', 'addDays', 'addHours', 'addMinutes', 'addSeconds',
        'convertFromUtc', 'convertToUtc', 'utcNow', 'parseDateTime',
        'base64', 'base64ToString', 'base64ToBinary',
        'uriComponent', 'uriComponentToString', 'dataUri', 'dataUriToBinary',
        'encodeUriComponent', 'decodeUriComponent',
        'createArray', 'item', 'items', 'iterationIndexes'
    ]
    
    def __init__(self):
        # Pattern to match Logic App expressions: @{...} or @someFunction(...)
        self.expression_pattern = re.compile(r'@\{[^}]+\}|@[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)')
        # Pattern to match function calls within expressions
        self.function_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
    
    def is_logic_app_workflow(self, content: str) -> bool:
        """
        Check if content is a Logic App workflow definition.
        
        Args:
            content: File content as string
            
        Returns:
            True if content appears to be a Logic App workflow
        """
        try:
            data = json.loads(content)
            
            # Check for ARM template with Logic App resources
            if 'resources' in data and isinstance(data.get('resources'), list):
                for resource in data['resources']:
                    if isinstance(resource, dict):
                        resource_type = resource.get('type', '')
                        if 'Microsoft.Logic/workflows' in resource_type:
                            return True
            
            # Check for Logic App indicators (direct workflow or definition wrapper)
            indicators = [
                # Standard Azure Logic App schema
                '$schema' in data and 'logic' in str(data.get('$schema', '')).lower(),
                # Workflow with definition wrapper
                'definition' in data and isinstance(data['definition'], dict) and 
                ('actions' in data['definition'] or 'triggers' in data['definition']),
                # Direct actions/triggers (could be dict or list)
                ('actions' in data and 'triggers' in data),
                # Has Logic App parameters with connections
                'parameters' in data and '$connections' in data.get('parameters', {}),
                # Check for staticResults (specific to Logic Apps)
                'staticResults' in data and ('actions' in data or 'definition' in data)
            ]
            
            return any(indicators)
        except (json.JSONDecodeError, TypeError):
            return False
    
    def parse_workflow(self, content: str) -> Optional[Dict]:
        """
        Parse a Logic App workflow definition.
        
        Args:
            content: Workflow JSON content
            
        Returns:
            Parsed workflow dictionary or None if invalid
        """
        try:
            workflow = json.loads(content)
            return workflow
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return None
    
    def extract_expressions_from_value(self, value, context: str = "") -> List[Dict]:
        """
        Extract expressions from a JSON value recursively.
        
        Args:
            value: JSON value (string, dict, list, etc.)
            context: Context path (e.g., 'actions.SendEmail.inputs.body')
            
        Returns:
            List of expression dictionaries
        """
        expressions = []
        
        if isinstance(value, str):
            # Find all expressions in the string
            matches = self.expression_pattern.findall(value)
            for match in matches:
                expr_info = self.analyze_expression(match)
                expr_info['context'] = context
                expr_info['full_string'] = value
                expressions.append(expr_info)
        
        elif isinstance(value, dict):
            for key, val in value.items():
                new_context = f"{context}.{key}" if context else key
                expressions.extend(self.extract_expressions_from_value(val, new_context))
        
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                new_context = f"{context}[{idx}]"
                expressions.extend(self.extract_expressions_from_value(item, new_context))
        
        return expressions
    
    def analyze_expression(self, expression: str) -> Dict:
        """
        Analyze a single Logic App expression.
        
        Args:
            expression: Expression string (e.g., "@{concat('Hello', variables('name'))}")
            
        Returns:
            Dictionary with expression analysis
        """
        # Remove @{ and } wrapper if present
        clean_expr = expression.strip()
        if clean_expr.startswith('@{') and clean_expr.endswith('}'):
            clean_expr = clean_expr[2:-1]
        elif clean_expr.startswith('@'):
            clean_expr = clean_expr[1:]
        
        # Extract function calls
        functions = self.function_pattern.findall(clean_expr)
        
        # Count nesting level (parentheses depth)
        nesting_level = max([clean_expr[:i+1].count('(') - clean_expr[:i+1].count(')') 
                            for i in range(len(clean_expr))], default=0)
        
        return {
            'raw_expression': expression,
            'clean_expression': clean_expr,
            'functions_used': functions,
            'function_count': len(functions),
            'nesting_level': nesting_level,
            'length': len(expression),
            'has_variables': 'variables(' in expression,
            'has_parameters': 'parameters(' in expression,
            'has_trigger': 'trigger' in expression.lower(),
            'has_actions': 'actions(' in expression or 'body(' in expression
        }
    
    def extract_all_expressions(self, workflow: Dict) -> List[Dict]:
        """
        Extract all expressions from a workflow definition.
        
        Args:
            workflow: Parsed workflow dictionary
            
        Returns:
            List of expression dictionaries
        """
        expressions = []
        
        # Handle ARM template format - extract Logic App from resources
        if 'resources' in workflow and isinstance(workflow.get('resources'), list):
            for resource in workflow['resources']:
                if isinstance(resource, dict) and 'Microsoft.Logic/workflows' in resource.get('type', ''):
                    # Extract the workflow properties
                    if 'properties' in resource:
                        workflow = resource['properties']
                        break
        
        # Check if workflow has a 'definition' wrapper
        if 'definition' in workflow:
            workflow = workflow['definition']
        
        # Extract from actions (handle both dict and list formats)
        if 'actions' in workflow:
            actions = workflow['actions']
            if isinstance(actions, dict):
                for action_name, action_def in actions.items():
                    context = f"actions.{action_name}"
                    expressions.extend(self.extract_expressions_from_value(action_def, context))
            elif isinstance(actions, list):
                for idx, action_def in enumerate(actions):
                    context = f"actions[{idx}]"
                    expressions.extend(self.extract_expressions_from_value(action_def, context))
        
        # Extract from triggers (handle both dict and list formats)
        if 'triggers' in workflow:
            triggers = workflow['triggers']
            if isinstance(triggers, dict):
                for trigger_name, trigger_def in triggers.items():
                    context = f"triggers.{trigger_name}"
                    expressions.extend(self.extract_expressions_from_value(trigger_def, context))
            elif isinstance(triggers, list):
                for idx, trigger_def in enumerate(triggers):
                    context = f"triggers[{idx}]"
                    expressions.extend(self.extract_expressions_from_value(trigger_def, context))
        
        # Extract from parameters
        if 'parameters' in workflow:
            context = "parameters"
            expressions.extend(self.extract_expressions_from_value(workflow['parameters'], context))
        
        # Extract from outputs
        if 'outputs' in workflow:
            context = "outputs"
            expressions.extend(self.extract_expressions_from_value(workflow['outputs'], context))
        
        return expressions
    
    def get_expression_statistics(self, expressions: List[Dict]) -> Dict:
        """
        Get statistics about extracted expressions.
        
        Args:
            expressions: List of expression dictionaries
            
        Returns:
            Statistics dictionary
        """
        if not expressions:
            return {
                'total_expressions': 0,
                'unique_expressions': 0,
                'function_usage': {},
                'avg_nesting_level': 0,
                'avg_length': 0
            }
        
        function_counts = defaultdict(int)
        for expr in expressions:
            for func in expr['functions_used']:
                function_counts[func] += 1
        
        unique_expressions = len(set(e['raw_expression'] for e in expressions))
        avg_nesting = sum(e['nesting_level'] for e in expressions) / len(expressions)
        avg_length = sum(e['length'] for e in expressions) / len(expressions)
        
        return {
            'total_expressions': len(expressions),
            'unique_expressions': unique_expressions,
            'function_usage': dict(sorted(function_counts.items(), key=lambda x: x[1], reverse=True)),
            'avg_nesting_level': round(avg_nesting, 2),
            'avg_length': round(avg_length, 2),
            'expressions_with_variables': sum(1 for e in expressions if e['has_variables']),
            'expressions_with_parameters': sum(1 for e in expressions if e['has_parameters']),
            'expressions_with_triggers': sum(1 for e in expressions if e['has_trigger']),
            'expressions_with_actions': sum(1 for e in expressions if e['has_actions'])
        }
    
    def create_training_sample(self, expression: Dict, workflow_context: Dict = None) -> Dict:
        """
        Create a training sample for fine-tuning.
        
        Args:
            expression: Expression dictionary from extract_all_expressions
            workflow_context: Optional workflow context for better descriptions
            
        Returns:
            Training sample with natural language description and expression
        """
        # Generate a basic natural language description
        description_parts = []
        
        # Describe the context
        if expression.get('context'):
            context = expression['context']
            if 'actions' in context:
                description_parts.append("In an action,")
            elif 'triggers' in context:
                description_parts.append("In a trigger,")
        
        # Describe what the expression does based on functions
        functions = expression.get('functions_used', [])
        if 'concat' in functions:
            description_parts.append("concatenate strings")
        if 'variables' in functions:
            description_parts.append("using a workflow variable")
        if 'parameters' in functions:
            description_parts.append("using a parameter")
        if any(f in functions for f in ['add', 'sub', 'mul', 'div']):
            description_parts.append("perform mathematical operation")
        if any(f in functions for f in ['formatDateTime', 'utcNow']):
            description_parts.append("format or manipulate date/time")
        
        description = " ".join(description_parts) if description_parts else "Use expression"
        
        return {
            'natural_language': description,
            'expression': expression['raw_expression'],
            'functions': expression['functions_used'],
            'context': expression.get('context', ''),
            'complexity': {
                'nesting_level': expression['nesting_level'],
                'function_count': expression['function_count']
            }
        }
    
    def generate_expression_descriptions(self, expression: str) -> List[str]:
        """
        Generate multiple natural language descriptions for an expression.
        This helps create more diverse training data.
        
        Args:
            expression: Logic App expression
            
        Returns:
            List of possible natural language descriptions
        """
        expr_info = self.analyze_expression(expression)
        descriptions = []
        functions = expr_info['functions_used']
        
        # Template-based descriptions
        if 'concat' in functions:
            descriptions.extend([
                "Concatenate multiple strings together",
                "Combine text values",
                "Join strings into one"
            ])
        
        if 'variables' in functions:
            descriptions.extend([
                "Get the value of a workflow variable",
                "Reference a variable",
                "Access variable data"
            ])
        
        if 'parameters' in functions:
            descriptions.extend([
                "Get a parameter value",
                "Reference a workflow parameter",
                "Access parameter data"
            ])
        
        if 'triggerBody' in functions or 'triggerOutputs' in functions:
            descriptions.extend([
                "Get data from the trigger",
                "Access trigger output",
                "Reference trigger body"
            ])
        
        if 'body' in functions:
            descriptions.extend([
                "Get the body of an action output",
                "Access action result body",
                "Reference action output body"
            ])
        
        # Generic fallback
        if not descriptions:
            descriptions.append(f"Expression using {', '.join(functions[:3])}" if functions else "Logic App expression")
        
        return descriptions[:5]  # Limit to top 5 descriptions
