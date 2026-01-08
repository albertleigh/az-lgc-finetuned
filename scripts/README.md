# Upload all models (GPT + BERT) at once
python scripts/upload_models_to_hf.py --username albertleigh --all

# Upload all as private repos
python scripts/upload_models_to_hf.py --username albertleigh --all --private

# Upload just the GPT model
python scripts/upload_models_to_hf.py --model models/azLgcExpGpt_HF --repo albertleigh/azlgc-gpt

# Upload just the BERT model
python scripts/upload_models_to_hf.py --model models/bert_classifier_azlgcexp_base --repo albertleigh/azlgc-bert-classifier