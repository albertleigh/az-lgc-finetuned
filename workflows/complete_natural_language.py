"""
Workflow to populate natural_language field for training samples using Azure OpenAI.
Reads training dataset files and generates concise natural language descriptions for each expression.
"""

import os
import json
import glob
import asyncio
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv
from openai import AzureOpenAI, AsyncAzureOpenAI
from tqdm import tqdm
from tqdm.asyncio import tqdm as async_tqdm
import time

# Load environment variables
load_dotenv()

class NaturalLanguageGenerator:
    """Generate natural language descriptions for Logic App expressions using Azure OpenAI."""
    
    def __init__(self, max_concurrent: int = 10):
        """Initialize Azure OpenAI client.
        
        Args:
            max_concurrent: Maximum number of concurrent API requests (default: 10)
        """
        self.client = AzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
        )
        self.async_client = AsyncAzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
        )
        self.deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'al-gpt-5')
        self.max_concurrent = max_concurrent
        
        print(f"✅ Initialized Azure OpenAI")
        print(f"   Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        print(f"   Deployment: {self.deployment}")
        print(f"   Max concurrent requests: {max_concurrent}")
    
    def generate_natural_language(self, expression: str, context: str = "", functions: List[str] = None) -> str:
        """
        Generate natural language description for a Logic App expression.
        
        Args:
            expression: The Logic App expression (e.g., "@items('For_each_ControlArea')")
            context: Context where the expression is used
            functions: List of functions used in the expression
            
        Returns:
            Natural language description
        """
        # Build context information
        context_info = ""
        if functions:
            context_info += f"\nFunctions used: {', '.join(functions)}"
        if context:
            # Extract the last part of context for brevity
            context_parts = context.split('.')
            context_info += f"\nUsed in: {context_parts[-1] if context_parts else context}"
        
        # Create prompt
        prompt = f"""You are an expert in Azure Logic Apps. Given a Logic App expression, generate a concise, natural language description of what it does.

Expression: {expression}{context_info}

Provide a short, clear description (1-2 sentences) that explains what this expression does in plain English. Focus on the action/data it represents, not the technical syntax.

Examples:
- "@items('For_each')" → "Get the current item in the For_each loop"
- "@parameters('param1')" → "Get the value of parameter param1"
- "@concat('Hello ', variables('name'))" → "Concatenate the text 'Hello ' with the value of variable name"
- "@triggerBody()?['data']" → "Get the data property from the trigger request body"

Natural language description:"""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are an expert in Azure Logic Apps who provides clear, concise explanations."},
                    {"role": "user", "content": prompt}
                ],
                # max_completion_tokens=200,
            )
            
            description = response.choices[0].message.content.strip()
            
            # Clean up the description
            # Remove quotes if AI added them
            if description.startswith('"') and description.endswith('"'):
                description = description[1:-1]
            if description.startswith("'") and description.endswith("'"):
                description = description[1:-1]
            
            return description
            
        except Exception as e:
            print(f"\n❌ Error generating description: {e}")
            return f"Logic App expression: {expression}"
    
    async def generate_natural_language_async(self, expression: str, context: str = "", functions: List[str] = None, semaphore: asyncio.Semaphore = None) -> str:
        """Async version of generate_natural_language for parallel processing."""
        if semaphore:
            async with semaphore:
                return await self._generate_natural_language_async_impl(expression, context, functions)
        else:
            return await self._generate_natural_language_async_impl(expression, context, functions)
    
    async def _generate_natural_language_async_impl(self, expression: str, context: str = "", functions: List[str] = None) -> str:
        """Implementation of async natural language generation."""
        # Build context information
        context_info = ""
        if functions:
            context_info += f"\nFunctions used: {', '.join(functions)}"
        if context:
            # Extract the last part of context for brevity
            context_parts = context.split('.')
            context_info += f"\nUsed in: {context_parts[-1] if context_parts else context}"
        
        # Create prompt
        prompt = f"""You are an expert in Azure Logic Apps. Given a Logic App expression, generate a concise, natural language description of what it does.

Expression: {expression}{context_info}

Provide a short, clear description (1-2 sentences) that explains what this expression does in plain English. Focus on the action/data it represents, not the technical syntax.

Examples:
- "@items('For_each')" → "Get the current item in the For_each loop"
- "@parameters('param1')" → "Get the value of parameter param1"
- "@concat('Hello ', variables('name'))" → "Concatenate the text 'Hello ' with the value of variable name"
- "@triggerBody()?['data']" → "Get the data property from the trigger request body"

Natural language description:"""

        try:
            response = await self.async_client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are an expert in Azure Logic Apps who provides clear, concise explanations."},
                    {"role": "user", "content": prompt}
                ],
                # max_completion_tokens=200,
            )
            
            description = response.choices[0].message.content.strip()
            
            # Clean up the description
            if description.startswith('"') and description.endswith('"'):
                description = description[1:-1]
            if description.startswith("'") and description.endswith("'"):
                description = description[1:-1]
            
            return description
            
        except Exception as e:
            return f"Logic App expression: {expression}"
    
    async def process_dataset_file_async(self, file_path: str, output_dir: str = None) -> Dict:
        """Async version of process_dataset_file for parallel processing."""
        print(f"\n{'='*70}")
        print(f"Processing: {Path(file_path).name}")
        print(f"{'='*70}")
        
        # Load dataset
        with open(file_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        print(f"Loaded {len(dataset)} samples")
        print(f"Processing with up to {self.max_concurrent} concurrent requests...")
        
        # Create semaphore for rate limiting
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Process each sample
        updated_count = 0
        error_count = 0
        
        async def process_sample(sample, idx):
            """Process a single sample."""
            nonlocal updated_count, error_count
            try:
                # Generate natural language description
                new_description = await self.generate_natural_language_async(
                    expression=sample['expression'],
                    context=sample.get('context', ''),
                    functions=sample.get('functions', []),
                    semaphore=semaphore
                )
                
                # Update the sample
                sample['natural_language'] = new_description
                sample['nl_updated_at'] = datetime.now().isoformat()
                updated_count += 1
                
            except Exception as e:
                error_count += 1
                if error_count <= 5:
                    tqdm.write(f"❌ Error processing sample {idx}: {e}")
        
        # Create tasks for all samples with progress bar
        tasks = [process_sample(sample, idx) for idx, sample in enumerate(dataset)]
        
        # Run all tasks concurrently with progress tracking
        for coro in async_tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Generating descriptions"):
            await coro

        # Save updated dataset
        if output_dir is None:
            # Save to same directory with _updated suffix
            base_path = Path(file_path)
            output_path = base_path.parent / f"{base_path.stem}_updated{base_path.suffix}"
        else:
            output_path = Path(output_dir) / Path(file_path).name
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved updated dataset to: {output_path}")
        print(f"   Updated: {updated_count}/{len(dataset)} samples")
        if error_count > 0:
            print(f"   Errors: {error_count}")
        
        return {
            'file': str(file_path),
            'total': len(dataset),
            'updated': updated_count,
            'errors': error_count,
            'output': str(output_path)
        }
    
    def process_dataset_file(self, file_path: str, output_dir: str = None) -> Dict:
        """
        Process a single training dataset file (sync wrapper for async version).
        
        Args:
            file_path: Path to the training dataset JSON file
            output_dir: Optional output directory (defaults to same location with _updated suffix)
            
        Returns:
            Dictionary with statistics
        """
        return asyncio.run(self.process_dataset_file_async(file_path, output_dir))
    
    def process_all_datasets(self, pattern: str = "datasets/training_dataset_*.json", output_dir: str = "datasets/updated") -> List[Dict]:
        """
        Process all training dataset files matching the pattern.
        
        Args:
            pattern: Glob pattern for dataset files
            output_dir: Output directory for updated files
            
        Returns:
            List of processing statistics for each file
        """
        files = glob.glob(pattern)
        
        if not files:
            print(f"❌ No files found matching pattern: {pattern}")
            return []
        
        print(f"\n{'='*70}")
        print(f"Found {len(files)} training dataset files")
        print(f"{'='*70}")
        
        for f in files:
            print(f"  - {Path(f).name}")
        
        print()
        
        results = []
        
        for file_path in files:
            try:
                result = self.process_dataset_file(file_path, output_dir)
                results.append(result)
            except Exception as e:
                print(f"\n❌ Failed to process {file_path}: {e}")
                results.append({
                    'file': str(file_path),
                    'error': str(e)
                })
        
        # Print summary
        print(f"\n{'='*70}")
        print("✨ PROCESSING COMPLETE")
        print(f"{'='*70}")
        
        total_samples = sum(r.get('total', 0) for r in results)
        total_updated = sum(r.get('updated', 0) for r in results)
        total_errors = sum(r.get('errors', 0) for r in results)
        
        print(f"\nSummary:")
        print(f"  Files processed: {len([r for r in results if 'error' not in r])}/{len(results)}")
        print(f"  Total samples: {total_samples}")
        print(f"  Successfully updated: {total_updated}")
        print(f"  Errors: {total_errors}")
        
        return results


def main():
    """Main workflow to generate natural language descriptions."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate natural language descriptions for Logic App expressions using Azure OpenAI'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        default='datasets/training_dataset_*.json',
        help='Glob pattern for training dataset files (default: datasets/training_dataset_*.json)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='datasets/updated',
        help='Output directory for updated files (default: datasets/updated)'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Process a single file instead of pattern matching'
    )
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=10,
        help='Maximum number of concurrent API requests (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    try:
        generator = NaturalLanguageGenerator(max_concurrent=args.max_concurrent)
    except Exception as e:
        print(f"❌ Failed to initialize Azure OpenAI client: {e}")
        print("\nMake sure you have set the following environment variables in .env:")
        print("  - AZURE_OPENAI_API_KEY")
        print("  - AZURE_OPENAI_ENDPOINT")
        print("  - AZURE_OPENAI_DEPLOYMENT")
        print("  - AZURE_OPENAI_API_VERSION (optional)")
        return
    
    # Process files
    if args.file:
        # Single file mode
        generator.process_dataset_file(args.file, args.output_dir)
    else:
        # Batch mode
        generator.process_all_datasets(args.pattern, args.output_dir)


if __name__ == '__main__':
    main()
