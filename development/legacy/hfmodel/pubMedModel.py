import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import requests
from development.legacy.model import hf_misc


# just an example for how we would later call the model through an API
def get_answer_from_model_BiobertBase(question):
    API_URL = "https://api-inference.huggingface.co/models/microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract"
    token = hf_misc.get_hf_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        # wait for response
        while response.status_code == 429:
            print("Waiting for available API calls...")
            time.sleep(10)
            response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    output = query({
        "inputs": question,
    })
    return output

# another example of an model just for testing
def get_answer_from_model_BiobertQA(question, context):
    API_URL = "https://api-inference.huggingface.co/models/Shushant/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext-ContaminationQAmodel_PubmedBERT"
    token = hf_misc.get_hf_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        # wait for response
        while response.status_code == 429:
            print("Waiting for available API calls...")
            time.sleep(10)
            response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    output = query({
        "inputs": {
            "question": question,
            "context": context
        }
    })
    return output["answer"]

# another example of an model just for testing
def get_answer_from_model_DistilBertBaseQA(question, context):
    API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-distilled-squad"
    token = hf_misc.get_hf_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        # wait for response
        while response.status_code == 429:
            print("Waiting for available API calls...")
            time.sleep(10)
            response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    output = query({
        "inputs": {
            "question": question,
            "context": context
        }
    })
    return output["answer"]
