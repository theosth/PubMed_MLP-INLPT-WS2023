# attach to the existing event loop when using jupyter notebooks
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy
import os
import openai
from tqdm import tqdm
from dotenv import load_dotenv
from answer_generation import GenAI
from langchain.schema import Document
import numpy as np
from datasets import Dataset
import json

if __name__ == "__main__":

    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    openai.api_key = api_key

    with open('development/evaluate/answering/question-context-pairs.json') as f:
        data = json.load(f)['questions']

    genai = GenAI()

    print("Running test set through answering model and evaluating results")
    results = []
    for q in tqdm(data):
        abstract = q['abstract_fragment']
        result = {
            'question': q['question'],
            'answer': genai.invoke([Document(page_content=abstract)], q['question']),
            'contexts': [abstract],
        }
        results.append(result)

    ds = Dataset.from_list(results)

    eval_res = evaluate(ds, metrics=[
        Faithfulness(),
        AnswerRelevancy()
    ])

    print(eval_res)
