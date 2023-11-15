import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datasets import load_dataset
from dotenv import load_dotenv
import os
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import json
import torch

def get_hf_access_token():
    """Load the access token from the .env.local file."""
    load_dotenv(dotenv_path=Path('.').absolute().parent / '.env.local')
    hf_token = os.getenv('HF_TOKEN')
    if hf_token:
        print("Hugging Face token loaded successfully.")
    else:
        print("Failed to load the Hugging Face token.")
    return hf_token

def get_dataset(dataset_name = 'theosth/PubMedScraped'):
    """Load a dataset from the Hugging Face Hub using the given token."""
    token = get_hf_access_token()
    dataset = load_dataset(dataset_name, token=token)

    return dataset

def get_model_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
    model = AutoModelForQuestionAnswering.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
    return model, tokenizer

def print_dataset_structure(dataset):
    for split in dataset.keys():
        print(f"\nStructure of {split} split:")
        print(dataset[split].column_names)

def reformat_dataset():
    dataset = get_dataset()
    extracted_documents = []
    for record in dataset['train']:
        documents = record['documents']
        extracted_documents.extend(documents)

    # save as json
    with open('reformatted_dataset.json', 'w', encoding='utf-8') as json_file:
        json.dump(extracted_documents, json_file, ensure_ascii=False, indent=4)

    print("Dataset has been reformatted and saved.")

if __name__ == "__main__":
    dataset = get_dataset()
    print_dataset_structure(dataset)
