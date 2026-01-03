"""
Quick demo of the Logic App expression parser (no GitHub token required).
"""

from scrapers import LogicAppExpressionParser
import json

def demo_expression_parser():
    """Demonstrate the expression parser with sample data."""
    
    print("=" * 70)
    print("Azure Logic App Expression Parser - Quick Demo")
    print("=" * 70)
    
    parser = LogicAppExpressionParser()
    
    # Sample expressions to test
    sample_expressions = [
        "@{concat('Hello', ' ', 'World')}",
        "@{variables('userName')}",
        "@{parameters('apiEndpoint')}",
        "@{triggerBody()?['data']?['email']}",
        "@{if(equals(variables('status'), 'active'), 'Yes', 'No')}",
        "@{formatDateTime(utcNow(), 'yyyy-MM-dd')}",
        "@{concat(toUpper(substring(variables('name'), 0, 1)), substring(variables('name'), 1))}",
        "@{body('HTTP_Action')?['results']}",
        "@{add(variables('count'), 1)}",
        "@{substring(variables('text'), 0, length(variables('text')))}",
    ]
    
    print("\n1. TESTING EXPRESSION PARSING")
    print("-" * 70)
    
    all_expressions = []
    for i, expr in enumerate(sample_expressions, 1):
        result = parser.analyze_expression(expr)
        all_expressions.append(result)
        
        print(f"\nExpression {i}: {expr}")
        print(f"  Functions: {', '.join(result['functions_used'])}")
        print(f"  Complexity: {result['function_count']} functions, nesting level {result['nesting_level']}")
        print(f"  Has variables: {result['has_variables']}")
        print(f"  Has parameters: {result['has_parameters']}")
    
    # Statistics
    print("\n\n2. EXPRESSION STATISTICS")
    print("-" * 70)
    
    stats = parser.get_expression_statistics(all_expressions)
    print(f"\nTotal expressions analyzed: {stats['total_expressions']}")
    print(f"Average nesting level: {stats['avg_nesting_level']}")
    print(f"Average length: {stats['avg_length']}")
    
    print(f"\nTop 5 functions used:")
    for i, (func, count) in enumerate(list(stats['function_usage'].items())[:5], 1):
        print(f"  {i}. {func}: {count} times")
    
    # Training samples
    print("\n\n3. GENERATING TRAINING SAMPLES")
    print("-" * 70)
    
    for i, expr in enumerate(all_expressions[:5], 1):
        sample = parser.create_training_sample(expr)
        print(f"\nSample {i}:")
        print(f"  NL Description: {sample['natural_language']}")
        print(f"  Expression: {sample['expression']}")
    
    # Complete workflow example
    print("\n\n4. PARSING A COMPLETE WORKFLOW")
    print("-" * 70)
    
    sample_workflow = {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "environment": {"type": "string", "defaultValue": "prod"}
        },
        "triggers": {
            "manual": {
                "type": "Request",
                "kind": "Http",
                "inputs": {"schema": {}}
            }
        },
        "actions": {
            "Initialize_name": {
                "type": "InitializeVariable",
                "inputs": {
                    "variables": [{
                        "name": "fullName",
                        "type": "string",
                        "value": "@{concat(triggerBody()?['firstName'], ' ', triggerBody()?['lastName'])}"
                    }]
                }
            },
            "Initialize_timestamp": {
                "type": "InitializeVariable",
                "inputs": {
                    "variables": [{
                        "name": "timestamp",
                        "type": "string",
                        "value": "@{formatDateTime(utcNow(), 'yyyy-MM-dd HH:mm:ss')}"
                    }]
                },
                "runAfter": {"Initialize_name": ["Succeeded"]}
            },
            "Compose_greeting": {
                "type": "Compose",
                "inputs": "@{concat('Hello ', variables('fullName'), '! Current time: ', variables('timestamp'))}",
                "runAfter": {"Initialize_timestamp": ["Succeeded"]}
            },
            "Condition": {
                "type": "If",
                "expression": {
                    "and": [{
                        "equals": ["@parameters('environment')", "prod"]
                    }]
                },
                "actions": {
                    "Log_production": {
                        "type": "Compose",
                        "inputs": "@{concat('Production mode: ', variables('fullName'))}"
                    }
                },
                "runAfter": {"Compose_greeting": ["Succeeded"]}
            }
        }
    }
    
    print("\nWorkflow structure:")
    print(f"  Triggers: {len(sample_workflow.get('triggers', {}))}")
    print(f"  Actions: {len(sample_workflow.get('actions', {}))}")
    print(f"  Parameters: {len(sample_workflow.get('parameters', {}))}")
    
    expressions = parser.extract_all_expressions(sample_workflow)
    print(f"\nExtracted {len(expressions)} expressions from workflow:")
    
    for i, expr in enumerate(expressions, 1):
        print(f"\n  {i}. {expr['raw_expression']}")
        print(f"     Context: {expr['context']}")
        print(f"     Functions: {', '.join(expr['functions_used'])}")
    
    # Save sample dataset
    print("\n\n5. CREATING SAMPLE DATASET")
    print("-" * 70)
    
    training_samples = []
    for expr in expressions:
        sample = parser.create_training_sample(expr)
        training_samples.append({
            'prompt': f"Translate this to Azure Logic App expression: {sample['natural_language']}",
            'completion': sample['expression'],
            'functions': sample['functions'],
            'complexity': sample['complexity']
        })
    
    # Save to file
    import os
    os.makedirs('datasets', exist_ok=True)
    
    output_file = 'datasets/demo_sample.jsonl'
    with open(output_file, 'w', encoding='utf-8') as f:
        for sample in training_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"\nCreated {len(training_samples)} training samples")
    print(f"Saved to: {output_file}")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("  1. Add your GitHub token to .env file")
    print("  2. Run: python scrape_logic_apps.py --max-files 50")
    print("  3. Check the datasets/ folder for output")
    print("\nOr explore more with: python examples/run_examples.py")


if __name__ == '__main__':
    demo_expression_parser()
