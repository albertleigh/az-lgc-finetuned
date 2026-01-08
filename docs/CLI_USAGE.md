# CLI Tools for Azure Logic App Expression Models

This project provides two CLI tools for interacting with the trained models:

1. **BERT Classifier CLI** - Classifies whether text is an Azure Logic App expression
2. **GPT Model CLI** - Generates Azure Logic App expressions from natural language

## Installation

Both CLIs are included in the project. Make sure you have the dependencies installed:

```bash
pip install -r requirements.txt
```

## BERT Classifier CLI

### Overview

The BERT classifier determines whether a given text is an Azure Logic App expression or not. It outputs a classification with confidence probabilities.

**Model**: `albertleigh/azlgc-bert-classifier` (or local: `models/bert_classifier_azlgcexp_base/`)

### Usage

#### Interactive REPL Mode

Start the interactive mode by running without arguments:

```bash
python clis/run_bert_model.py
```

This opens an interactive prompt where you can:
- Type or paste text to classify
- Use commands like `/help`, `/exit`, `/clear`
- Get real-time classification results

**Example Session**:
```
> @{body('Parse_JSON')?['content']?['main_text']}

============================================================
Result: Azure Logic App Expression
============================================================
Non-Azure Logic App: 0.0234 (2.34%)
Azure Logic App:     0.9766 (97.66%)

> print("Hello World")

============================================================
Result: Non-Azure Logic App Expression
============================================================
Non-Azure Logic App: 0.9823 (98.23%)
Azure Logic App:     0.0177 (1.77%)
```

#### Single Query Mode

Classify a single expression without entering interactive mode:

```bash
python clis/run_bert_model.py -t "@{body('Parse_JSON')?['content']?['main_text']}"
```

**Output**:
```
Loading model... ✓

Result: Azure Logic App Expression
Non-Azure Logic App: 0.0234 (2.34%)
Azure Logic App:     0.9766 (97.66%)
```

#### Using a Different Model

Specify a custom model path or HuggingFace model ID:

```bash
# Local model
python clis/run_bert_model.py --model-path models/bert_classifier_azlgcexp_base

# HuggingFace model
python clis/run_bert_model.py --model-path albertleigh/azlgc-bert-classifier
```

### Command Reference

```bash
python clis/run_bert_model.py [OPTIONS]

Options:
  -t, --text TEXT        Single text to classify (non-interactive mode)
  --model-path PATH      Path to model directory or HuggingFace model ID
                        (default: albertleigh/azlgc-bert-classifier)
  -h, --help            Show help message
```

### REPL Commands

| Command | Description |
|---------|-------------|
| `/exit`, `/quit` | Exit the program |
| `/help` | Show help message |
| `/clear` | Clear the screen |

### Use Cases

1. **Validate scraped expressions**: Check if scraped code is actually an Azure Logic App expression
2. **Filter datasets**: Identify and remove non-Logic App expressions from training data
3. **Quality control**: Verify expression quality before adding to production workflows

---

## GPT Model CLI

### Overview

The GPT model generates Azure Logic App expressions from natural language descriptions. Fine-tuned on GPT-2, it understands Logic App syntax and common patterns.

**Model**: `albertleigh/azlgc-gpt` (or local: `models/azLgcExpGpt_HF/`)

### Usage

#### Interactive REPL Mode

Start the interactive mode:

```bash
python clis/run_gpt_model.py
```

**Example Session**:
```
> QUESTION: Get the value of the variable ContributionsAdded.

QUESTION: Get the value of the variable ContributionsAdded. ANSWER: @{variables('ContributionsAdded')}

> QUESTION: Concatenate the strings "Hello" and "World".

QUESTION: Concatenate the strings "Hello" and "World". ANSWER: @{concat('Hello', 'World')}
```

#### Single Query Mode

Generate a response for a single prompt:

```bash
python clis/run_gpt_model.py -p "QUESTION: Get the value of the variable ContributionsAdded."
```

**Output**:
```
Loading model... ✓
QUESTION: Get the value of the variable ContributionsAdded. ANSWER: @{variables('ContributionsAdded')}
```

#### Custom Max Length

Control the maximum output length (in tokens):

```bash
python clis/run_gpt_model.py --max-length 100
```

Or interactively:
```
> /max 150
Max length set to 150 tokens
```

#### Using a Different Model

```bash
# Local model
python clis/run_gpt_model.py --model-path models/azLgcExpGpt_HF

# HuggingFace model
python clis/run_gpt_model.py --model-path albertleigh/azlgc-gpt
```

### Command Reference

```bash
python clis/run_gpt_model.py [OPTIONS]

Options:
  -p, --prompt TEXT      Single prompt to generate (non-interactive mode)
  --max-length INT       Maximum output length in tokens (default: 256)
  --model-path PATH      Path to model directory or HuggingFace model ID
                        (default: albertleigh/azlgc-gpt)
  -h, --help            Show help message
```

### REPL Commands

| Command | Description |
|---------|-------------|
| `/exit`, `/quit` | Exit the program |
| `/help` | Show help message |
| `/clear` | Clear the screen |
| `/max N` | Set max output length to N tokens |

### Prompt Format

The model is trained on prompts in the format:
```
QUESTION: [natural language description] ANSWER: [expression]
```

For best results, start your prompts with "QUESTION:" and the model will generate "ANSWER:" followed by the expression.

### Use Cases

1. **Expression generation**: Convert natural language to Logic App expressions
2. **Learning tool**: Understand how to write complex expressions
3. **Prototyping**: Quickly generate expression syntax for new workflows
4. **Documentation**: Generate examples for training materials

---

## Comparing the Two Models

| Feature | BERT Classifier | GPT Generator |
|---------|----------------|---------------|
| **Task** | Binary classification | Text generation |
| **Input** | Any text | Natural language question |
| **Output** | Classification + probabilities | Logic App expression |
| **Use Case** | Validation, filtering | Generation, prototyping |
| **Speed** | Very fast | Fast |
| **Model Size** | ~110M parameters | ~124M parameters |

## Performance Tips

### BERT Classifier
- **Fast inference**: Typically < 100ms per classification
- **Batch processing**: Modify the script to process multiple texts
- **No GPU required**: Works well on CPU for most use cases

### GPT Generator
- **Adjust max_length**: Lower values (50-100) for faster generation
- **Prompt engineering**: Start with "QUESTION:" for best results
- **Temperature control**: Not exposed in CLI, but can be modified in code
- **GPU recommended**: For faster generation, especially with larger prompts

## Troubleshooting

### Model Loading Issues

**Problem**: `OSError: Unable to load weights from pytorch model file`

**Solution**:
1. Check model path is correct
2. Re-download from HuggingFace:
   ```bash
   python -c "from transformers import AutoModelForSequenceClassification; AutoModelForSequenceClassification.from_pretrained('albertleigh/azlgc-bert-classifier')"
   ```

### Slow Performance

**Problem**: Model takes a long time to load or run

**Solution**:
- First run downloads model from HuggingFace (can take time)
- Subsequent runs use cached models
- For GPT model, reduce `--max-length`
- Consider using GPU if available

### Unexpected Output Format

**Problem**: GPT model doesn't generate expected format

**Solution**:
- Ensure prompt starts with "QUESTION:"
- Increase `--max-length` if output is truncated
- Model generates in format: `QUESTION: ... ANSWER: ...`

### Out of Memory

**Problem**: `RuntimeError: CUDA out of memory` or similar

**Solution**:
- Reduce `--max-length` for GPT model
- Use CPU instead of GPU
- Close other applications

## Python API Usage

Both CLIs can be imported and used in Python code:

### BERT Classifier

```python
from clis.run_bert_model import BERTClassifierCLI

# Initialize
classifier = BERTClassifierCLI('albertleigh/azlgc-bert-classifier')

# Classify
text = "@{variables('myVar')}"
classification, non_az_prob, az_prob = classifier.classify(text)

print(f"{classification}: {az_prob:.2%}")
# Output: Azure Logic App Expression: 97.66%
```

### GPT Generator

```python
from clis.run_gpt_model import GPTModelCLI

# Initialize
generator = GPTModelCLI('albertleigh/azlgc-gpt', max_length=256)

# Generate
prompt = "QUESTION: Get the trigger body."
result = generator.generate(prompt)

print(result)
# Output: QUESTION: Get the trigger body. ANSWER: @{triggerBody()}
```

## Next Steps

- **Training**: See [MODEL_TRAINING.md](MODEL_TRAINING.md) for how these models were trained
- **Notebooks**: Check [notebooks/](../notebooks/) for training notebooks
- **API Integration**: Use the Python API to integrate models into your workflows
- **Fine-tuning**: Retrain models with your own datasets

## Model Credits

Both models are fine-tuned versions trained on the Azure Logic App expressions dataset:
- Base models: `bert-base-uncased`, `gpt2`
- Dataset: [albertleigh/az-logic-apps-dataset](https://huggingface.co/datasets/albertleigh/az-logic-apps-dataset)
- Published models: Available on [HuggingFace](https://huggingface.co/albertleigh)
