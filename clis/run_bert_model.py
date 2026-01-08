#!/usr/bin/env python
"""
AzLgcExp BERT CLI - Interactive REPL for Azure Logic App Expression Classification
"""
import sys
import argparse
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import warnings

warnings.filterwarnings('ignore')


class BERTClassifierCLI:
    def __init__(self, model_path: str):
        """Initialize the model and tokenizer."""
        print("Loading model... ", end='', flush=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        print("✓")

    def classify(self, text: str) -> tuple[str, float, float]:
        """
        Classify whether text is an Azure Logic App expression.
        
        Returns:
            tuple: (classification, non_az_prob, az_prob)
                - classification: "Azure Logic App Expression" or "Non-Azure Logic App Expression"
                - non_az_prob: probability it's NOT an az logical expression
                - az_prob: probability it IS an az logical expression
        """
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model(**inputs)
        predictions = torch.softmax(outputs.logits, dim=-1)

        non_az_prob = predictions[0][0].item()
        az_prob = predictions[0][1].item()

        if non_az_prob > az_prob:
            classification = "Non-Azure Logic App Expression"
        else:
            classification = "Azure Logic App Expression"

        return classification, non_az_prob, az_prob

    def repl(self):
        """Run interactive REPL."""
        print("\n" + "=" * 60)
        print("AzLgcExp BERT Classifier - Interactive CLI")
        print("=" * 60)
        print("\nThis tool classifies whether text is an Azure Logic App expression.")
        print("\nCommands:")
        print("  /exit, /quit - Exit the program")
        print("  /help        - Show this help")
        print("  /clear       - Clear screen")
        print("\nType your text and press Enter to classify.\n")

        while True:
            try:
                text = input("\n> ").strip()

                if not text:
                    continue

                # Handle commands
                if text.lower() in ['/exit', '/quit']:
                    print("Goodbye!")
                    break
                elif text.lower() == '/help':
                    print("\nCommands:")
                    print("  /exit, /quit - Exit the program")
                    print("  /help        - Show this help")
                    print("  /clear       - Clear screen")
                    continue
                elif text.lower() == '/clear':
                    print("\033[2J\033[H", end='')  # Clear screen
                    continue

                # Classify text
                print("\nClassifying... ", end='', flush=True)
                classification, non_az_prob, az_prob = self.classify(text)
                print("\r" + " " * 20 + "\r", end='')  # Clear "Classifying..."

                print(f"\n{'=' * 60}")
                print(f"Result: {classification}")
                print(f"{'=' * 60}")
                print(f"Non-Azure Logic App: {non_az_prob:.4f} ({non_az_prob * 100:.2f}%)")
                print(f"Azure Logic App:     {az_prob:.4f} ({az_prob * 100:.2f}%)")

            except KeyboardInterrupt:
                print("\n\nUse /exit or /quit to exit")
                continue
            except EOFError:
                print("\nGoodbye!")
                break


def main():
    parser = argparse.ArgumentParser(
        description='AzLgcExp BERT CLI - Azure Logic App Expression Classifier',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive REPL mode
  %(prog)s

  # Single query mode
  %(prog)s -t "@{body('Parse_JSON')?['content']?['main_text']}"

  # Classify multiple expressions
  %(prog)s -t "tokenizer(text, return_tensors='pt')"
        """
    )
    parser.add_argument(
        '-t', '--text',
        type=str,
        help='Single text to classify (non-interactive mode)'
    )
    parser.add_argument(
        '--model-path',
        type=str,
        default='albertleigh/azlgc-bert-classifier',
        help='Path to the model directory or HuggingFace model ID (default: albertleigh/bert_classifier_azlgcexp_base)'
    )

    args = parser.parse_args()

    # Initialize CLI
    cli = BERTClassifierCLI(args.model_path)

    # Single text mode or REPL mode
    if args.text:
        classification, non_az_prob, az_prob = cli.classify(args.text)
        print(f"\nResult: {classification}")
        print(f"Non-Azure Logic App: {non_az_prob:.4f} ({non_az_prob * 100:.2f}%)")
        print(f"Azure Logic App:     {az_prob:.4f} ({az_prob * 100:.2f}%)")
    else:
        cli.repl()


if __name__ == '__main__':
    main()
