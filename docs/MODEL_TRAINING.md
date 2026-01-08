# Model Training Notebooks

This project includes two Jupyter notebooks for training the Azure Logic App expression models:

1. **BERT Classifier** ([az_lgc_exp_catagory_bert.ipynb](../notebooks/az_lgc_exp_catagory_bert.ipynb)) - Binary classification model
2. **GPT-2 Generator** ([az_lgc_exp_gpt2.ipynb](../notebooks/az_lgc_exp_gpt2.ipynb)) - Causal language model for expression generation

## Prerequisites

### Environment Setup

```bash
# Install required packages
pip install datasets transformers torch matplotlib numpy
pip install "protobuf<5.0.0"  # For compatibility

# Optional: For GPU training
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Dataset

Both notebooks use the HuggingFace dataset: [`albertleigh/az-logic-apps-dataset`](https://huggingface.co/datasets/albertleigh/az-logic-apps-dataset)

- **BERT**: Uses `categorization/training_dataset_categorization_v1.parquet`
- **GPT-2**: Uses `train/training_dataset_v1.parquet`

---

## BERT Classifier Notebook

**File**: [notebooks/az_lgc_exp_catagory_bert.ipynb](../notebooks/az_lgc_exp_catagory_bert.ipynb)

### Purpose

Train a binary classifier to distinguish between Azure Logic App expressions and non-Logic App code.

### Dataset Format

The categorization dataset contains:
```python
{
  'expression': str,      # The code/expression text
  'complete': bool       # True if Azure Logic App expression, False otherwise
}
```

### Training Process

#### 1. **Setup & Data Loading**
- Loads `bert-base-uncased` tokenizer and model
- Imports categorization dataset from HuggingFace
- Splits data into train/test (90%/10%)

#### 2. **Data Analysis**
- Analyzes expression length distribution
- Visualizes Azure Logic App vs non-Logic App expressions
- Determines optimal sequence length

**Key Statistics**:
- Dataset size: ~thousands of samples
- Label distribution: Balanced between Azure Logic App and other expressions
- Max sequence length: 512 tokens (BERT limit)

#### 3. **Model Architecture**
```python
class BertClassifier(nn.Module):
    def __init__(self, bert_model, num_classes=2):
        super().__init__()
        self.bert = bert_model
        self.classifier = nn.Linear(768, num_classes)  # 768 = BERT hidden size
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]  # [CLS] token
        return self.classifier(cls_output)
```

#### 4. **Training Configuration**
- **Optimizer**: AdamW
- **Learning Rate**: 2e-5 (typical for BERT fine-tuning)
- **Batch Size**: 16-32 (depending on GPU memory)
- **Epochs**: 3-5
- **Loss**: CrossEntropyLoss

#### 5. **Training Loop**
- Forward pass through BERT + classifier
- Compute loss and accuracy
- Backpropagation and optimization
- Track training and validation metrics

#### 6. **Evaluation**
- Test set accuracy: ~95-98%
- Confusion matrix visualization
- Per-class precision, recall, F1-score

#### 7. **Model Export**
```python
# Save to local directory
model.save_pretrained('models/bert_classifier_azlgcexp_base')
tokenizer.save_pretrained('models/bert_classifier_azlgcexp_base')

# Push to HuggingFace Hub
model.push_to_hub('albertleigh/azlgc-bert-classifier')
tokenizer.push_to_hub('albertleigh/azlgc-bert-classifier')
```

### Running the Notebook

1. **Open in VS Code**:
   ```bash
   code notebooks/az_lgc_exp_catagory_bert.ipynb
   ```

2. **Select Python kernel**: Choose a kernel with transformers installed

3. **Run cells sequentially**: Execute cells from top to bottom

4. **Monitor training**: Watch loss/accuracy in outputs

5. **Adjust hyperparameters** (optional):
   - Learning rate: Cell with `learning_rate` variable
   - Batch size: Cell with `batch_size` variable
   - Epochs: Cell with training loop

### Expected Results

- **Training time**: 10-30 minutes (GPU), 1-2 hours (CPU)
- **Final accuracy**: 95-98% on test set
- **Model size**: ~110MB (BERT-base parameters)

### Key Cells

| Cell # | Description |
|--------|-------------|
| 1-3 | Imports and setup |
| 4-6 | Load and split dataset |
| 7-8 | Data analysis and visualization |
| 9-13 | Model architecture definition |
| 14-17 | Training loop |
| 18-20 | Evaluation and metrics |
| 21-24 | Model saving and export |

---

## GPT-2 Generator Notebook

**File**: [notebooks/az_lgc_exp_gpt2.ipynb](../notebooks/az_lgc_exp_gpt2.ipynb)

### Purpose

Fine-tune GPT-2 to generate Azure Logic App expressions from natural language descriptions.

### Dataset Format

The training dataset contains:
```python
{
  'natural_language': str,  # Natural language description
  'expression': str         # Azure Logic App expression
}
```

### Training Process

#### 1. **Setup & Data Loading**
- Loads `gpt2` model and tokenizer
- Imports training dataset from HuggingFace
- Configures tokenizer with padding token

#### 2. **Data Preprocessing**
- Analyzes input/output length distribution
- Filters samples by combined length (≤ 256 tokens)
- Creates training prompts in format: `QUESTION: [nl] ANSWER: [expr]`

**Sample Format**:
```
QUESTION: Get the value of the variable ContributionsAdded. ANSWER: @{variables('ContributionsAdded')}
```

#### 3. **Length Analysis**
```python
# Visualize token length distribution
seq_len = 256  # Maximum sequence length
# Filter: natural_language_len + expression_len <= seq_len
```

#### 4. **Model Configuration**
- **Base Model**: `gpt2` (124M parameters)
- **Alternative**: `gpt2-large` (774M, commented out)
- **Sequence Length**: 256 tokens
- **Padding**: Uses EOS token as pad token

#### 5. **Training Configuration**
- **Optimizer**: AdamW
- **Learning Rate**: 5e-5 (slightly higher than BERT)
- **Batch Size**: 32
- **Epochs**: 3-5
- **Loss**: Causal Language Modeling loss (CrossEntropy)

#### 6. **Training Loop**
- Tokenize input as: `QUESTION: [nl] ANSWER: [expr]`
- Forward pass through GPT-2
- Compute loss on target tokens only (ANSWER part)
- Track perplexity and loss

#### 7. **Evaluation**
- Generate sample expressions from prompts
- Compare generated vs ground truth
- Measure BLEU score, exact match rate

**Sample Generations**:
```
Input:  QUESTION: Get the trigger body.
Output: ANSWER: @{triggerBody()}

Input:  QUESTION: Concatenate first name and last name variables.
Output: ANSWER: @{concat(variables('firstName'), ' ', variables('lastName'))}
```

#### 8. **Model Export**
```python
# Save to local directory
model.save_pretrained('models/azLgcExpGpt_HF')
tokenizer.save_pretrained('models/azLgcExpGpt_HF')

# Push to HuggingFace Hub
model.push_to_hub('albertleigh/azlgc-gpt')
tokenizer.push_to_hub('albertleigh/azlgc-gpt')
```

### Running the Notebook

1. **Open in VS Code**:
   ```bash
   code notebooks/az_lgc_exp_gpt2.ipynb
   ```

2. **Select Python kernel**: Choose a kernel with PyTorch and transformers

3. **Run cells sequentially**: Execute from top to bottom

4. **Monitor generation quality**: Check sample outputs during training

5. **Adjust hyperparameters** (optional):
   - Sequence length: `seq_len = 256`
   - Batch size: `batch_size = 32`
   - Learning rate: In optimizer configuration

### Expected Results

- **Training time**: 20-60 minutes (GPU), 2-4 hours (CPU)
- **Perplexity**: ~1.5-2.5 (lower is better)
- **Generation quality**: 70-85% syntactically correct expressions
- **Model size**: ~500MB (GPT-2 parameters)

### Key Cells

| Cell # | Description |
|--------|-------------|
| 1-4 | Imports, model loading, hyperparameters |
| 5-9 | Load dataset and analyze lengths |
| 10-13 | Data preprocessing and filtering |
| 14-17 | Tokenization and prompt formatting |
| 18 | Markdown: Training section |
| 19-22 | Training loop implementation |
| 23-26 | Generation evaluation |
| 27-28 | Model saving and export |

---

## Comparison: BERT vs GPT-2 Training

| Aspect | BERT Classifier | GPT-2 Generator |
|--------|----------------|-----------------|
| **Task** | Classification | Generation |
| **Architecture** | Encoder-only | Decoder-only |
| **Input** | Single expression | Question-answer pairs |
| **Output** | Binary label | Generated text |
| **Training Time** | Faster (10-30 min) | Slower (20-60 min) |
| **Complexity** | Simpler | More complex |
| **Evaluation** | Accuracy, F1 | Perplexity, BLEU |
| **Use Case** | Validation | Expression creation |

---

## Tips for Training

### General Tips

1. **Start Small**: Test with 1 epoch first to verify everything works
2. **Monitor Metrics**: Watch loss curves for overfitting
3. **Use GPU**: Training is 10-50x faster on GPU
4. **Save Checkpoints**: Save model every epoch in case of crashes
5. **Version Control**: Track hyperparameters and results

### BERT Classifier Tips

- **Class Imbalance**: Ensure balanced dataset for best results
- **Sequence Length**: Most expressions fit in 256 tokens
- **Learning Rate**: 2e-5 is standard; try 1e-5 to 5e-5 range
- **Frozen Layers**: Can freeze early BERT layers for faster training

### GPT-2 Generator Tips

- **Prompt Format**: Consistent "QUESTION: ... ANSWER: ..." format is crucial
- **Sequence Length**: 256 tokens balances quality and speed
- **Batch Size**: Reduce if out of memory (try 16 or 8)
- **Temperature**: Add temperature control for more diverse outputs
- **Beam Search**: Use during inference for better quality (not in training)

---

## Troubleshooting

### Out of Memory Errors

**Symptoms**: `RuntimeError: CUDA out of memory`

**Solutions**:
```python
# Reduce batch size
batch_size = 16  # or 8, 4

# Use gradient accumulation
accumulation_steps = 4

# Use mixed precision training (PyTorch 1.6+)
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()
```

### Slow Training

**Solutions**:
- Use GPU (CUDA)
- Reduce sequence length
- Increase batch size (if memory allows)
- Use DataLoader with `num_workers > 0`

### Poor Model Performance

**BERT Classifier**:
- Check class balance in dataset
- Increase training epochs (try 5-10)
- Add more training data
- Try different learning rates

**GPT-2 Generator**:
- Verify prompt format consistency
- Increase training epochs
- Check for data quality issues
- Try `gpt2-medium` or `gpt2-large` for better results

### Model Not Saving

**Problem**: Errors when saving to HuggingFace Hub

**Solutions**:
```bash
# Login to HuggingFace
huggingface-cli login

# Or use environment variable
export HUGGINGFACE_TOKEN=your_token_here

# Or in notebook
from huggingface_hub import notebook_login
notebook_login()
```

---

## Customization Guide

### Training on Your Own Data

#### BERT Classifier

1. **Prepare dataset**:
   ```python
   data = {
       'expression': ['@{variables("x")}', 'print("hello")', ...],
       'complete': [True, False, ...]  # True = Logic App expression
   }
   ```

2. **Convert to HuggingFace Dataset**:
   ```python
   from datasets import Dataset
   dataset = Dataset.from_dict(data)
   ```

3. **Update notebook**: Replace `load_dataset()` call with your dataset

#### GPT-2 Generator

1. **Prepare dataset**:
   ```python
   data = {
       'natural_language': ['Get variable x', 'Concatenate a and b', ...],
       'expression': ['@{variables("x")}', '@{concat(a, b)}', ...]
   }
   ```

2. **Format as Question-Answer**:
   ```python
   data['prompt'] = [
       f"QUESTION: {nl} ANSWER: {expr}"
       for nl, expr in zip(data['natural_language'], data['expression'])
   ]
   ```

3. **Update notebook**: Replace dataset loading and preprocessing

### Hyperparameter Tuning

Create a parameter grid and train multiple models:

```python
learning_rates = [1e-5, 2e-5, 5e-5]
batch_sizes = [16, 32]
epochs = [3, 5]

for lr in learning_rates:
    for bs in batch_sizes:
        for ep in epochs:
            # Train model with these parameters
            # Save results
```

---

## Model Deployment

After training, deploy models:

1. **Local Usage**: Models saved in `models/` directory
2. **HuggingFace Hub**: Push with `push_to_hub()`
3. **CLI Tools**: Use with [CLI_USAGE.md](CLI_USAGE.md)
4. **API Integration**: Import model classes in Python

See [CLI_USAGE.md](CLI_USAGE.md) for using trained models.

---

## Additional Resources

- **Transformers Documentation**: https://huggingface.co/docs/transformers
- **BERT Paper**: https://arxiv.org/abs/1810.04805
- **GPT-2 Paper**: https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
- **Dataset**: https://huggingface.co/datasets/albertleigh/az-logic-apps-dataset
- **Models**: https://huggingface.co/albertleigh

## Next Steps

1. **Run Notebooks**: Train models on your data
2. **Evaluate Results**: Test on your use cases
3. **Use CLI Tools**: Deploy trained models ([CLI_USAGE.md](CLI_USAGE.md))
4. **Fine-tune Further**: Retrain with domain-specific data
