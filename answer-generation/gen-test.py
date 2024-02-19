import os
from transformers import AutoTokenizer
from dotenv import load_dotenv

# load environment variables from .env file
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv(raise_error_if_not_found=True))
#tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-13b-chat-hf", token=os.getenv("HF_AUTH"))

import ollama

resp = ollama.generate(model='llama2', )
print(resp)