#!/usr/bin/env python
"""
AzLgcExp GPT CLI - Interactive REPL for GPT-2 based model
"""
import sys
import argparse
from transformers import AutoModelForCausalLM, AutoTokenizer
import warnings

warnings.filterwarnings('ignore')


class GPTModelCLI:
    def __init__(self, model_path: str, max_length: int = 256):
        """Initialize the model and tokenizer."""
        print("Loading model... ", end='', flush=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.max_length = max_length
        print("✓")

    def generate(self, prompt: str, max_length: int = None) -> str:
        """Generate text from the prompt."""
        if max_length is None:
            max_length = self.max_length

        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            pad_token_id=self.tokenizer.eos_token_id
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def repl(self):
        """Run interactive REPL."""
        print("\n" + "=" * 60)
        print("AzLgcExp Interactive CLI")
        print("=" * 60)
        print("\nCommands:")
        print("  /exit, /quit - Exit the program")
        print("  /help        - Show this help")
        print("  /clear       - Clear screen")
        print("  /max N       - Set max output length to N tokens")
        print("\nType your prompt and press Enter to generate.\n")

        while True:
            try:
                prompt = input("\n> ").strip()

                if not prompt:
                    continue

                # Handle commands
                if prompt.lower() in ['/exit', '/quit']:
                    print("Goodbye!")
                    break
                elif prompt.lower() == '/help':
                    print("\nCommands:")
                    print("  /exit, /quit - Exit the program")
                    print("  /help        - Show this help")
                    print("  /clear       - Clear screen")
                    print("  /max N       - Set max output length to N tokens")
                    continue
                elif prompt.lower() == '/clear':
                    print("\033[2J\033[H", end='')  # Clear screen
                    continue
                elif prompt.lower().startswith('/max '):
                    try:
                        new_max = int(prompt.split()[1])
                        self.max_length = new_max
                        print(f"Max length set to {new_max} tokens")
                    except (IndexError, ValueError):
                        print("Usage: /max <number>")
                    continue

                # Generate response
                print("\nGenerating... ", end='', flush=True)
                response = self.generate(prompt)
                print("\r" + " " * 20 + "\r", end='')  # Clear "Generating..."
                print(response)

            except KeyboardInterrupt:
                print("\n\nUse /exit or /quit to exit")
                continue
            except EOFError:
                print("\nGoodbye!")
                break


def main():
    parser = argparse.ArgumentParser(
        description='AzLgcExp GPT CLI - Interactive text generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive REPL mode
  %(prog)s

  # Single query mode
  %(prog)s -p "QUESTION: Get the value of the variable ContributionsAdded."

  # Set custom max length
  %(prog)s --max-length 100
        """
    )
    parser.add_argument(
        '-p', '--prompt',
        type=str,
        help='Single prompt to generate (non-interactive mode)'
    )
    parser.add_argument(
        '--max-length',
        type=int,
        default=256,
        help='Maximum output length in tokens (default: 256)'
    )
    parser.add_argument(
        '--model-path',
        type=str,
        default='Q:/home/azLgcExp/azLgcExpGpt_HF',
        help='Path to the model directory'
    )

    args = parser.parse_args()

    # Initialize CLI
    cli = GPTModelCLI(args.model_path, args.max_length)

    # Single prompt mode or REPL mode
    if args.prompt:
        result = cli.generate(args.prompt)
        print(result)
    else:
        cli.repl()


if __name__ == '__main__':
    main()
