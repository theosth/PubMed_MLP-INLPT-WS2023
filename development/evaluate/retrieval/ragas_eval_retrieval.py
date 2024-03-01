import os
import sys
import json
from pathlib import Path

import openai
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv
from datasets import Dataset

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from development.commons import env
from development.answer.answer_generation import GenAI
from development.retrieve.retrieval_wrapper import CustomOpensearchRetriever
from ragas import evaluate
from ragas.metrics import ContextPrecision, ContextRecall, ContextRelevancy
from langchain.schema import Document


def prepare_dataset(
    retrieval_dataset_path: str = env.RETRIEVAL_TESTSET_PATH,
    max_elements: int = None,
) -> Dataset:
    with open(retrieval_dataset_path, "r") as f:
        data = json.load(f)["questions"]

    # Limit the data to max_elements if it set
    if max_elements is not None:
        data = data[:max_elements]

    genai = GenAI()
    retriever = CustomOpensearchRetriever()
    print("Running test set through answering model and evaluating results")
    results = []
    for elm in tqdm(data):
        abstract = elm["abstract_fragment"]
        result = {
            "question": elm["question"],
            # "answer": genai.invoke([Document(page_content=abstract)], elm["question"]),
            "contexts": [
                document.page_content
                for document in retriever.get_relevant_documents(query=elm["question"])
            ],
        }
        results.append(result)

    return Dataset.from_list(results)


def evaluate_retrieval(
    dataset: Dataset,
    retrieval_eval_result_path: str = env.RETRIEVAL_RAGAS_EVAL_RESULT_PATH,
    max_elements: int = None,
) -> dict:

    # first check if the file path is valid with a sample json
    try:
        with open(retrieval_eval_result_path, "w") as f:
            json.dump(
                {"message": "Retrieval Ragas Result filepath is valid"}, f, indent=2
            )
    except Exception as e:
        print(f"Error: {e}")
        return
    print("Filepath is valid")

    # cut off the dataset if max_elements is set
    if max_elements is not None:
        dataset = dataset.select(range(max_elements))
        # safety check since this can get expensive ^^
        if len(dataset) > max_elements:
            throw(
                f"Dataset is larger than max_elements: {len(dataset)} > {max_elements}"
            )

    evaluation_results = evaluate(dataset, metrics=[ContextRelevancy()])
    # save to file
    evaluation_results.to_pandas().to_json(
        retrieval_eval_result_path, orient="records", indent=2
    )


if __name__ == "__main__":
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    openai.api_key = api_key

    # dataset = prepare_dataset(max_elements=1)

    # for testing
    # dataset = Dataset.from_list(
    #     [
    #         {
    #             "question": "What is the prevalence of attention deficit hyperactivity disorder (ADHD) in adults with autism spectrum disorders (ASDs) compared to the general adult population?",
    #             "contexts": [
    #                 'Features of attention deficit hyperactivity disorder (ADHD) and impairments on neuropsychological, tests of attention have been documented in children with autism spectrum disorders (ASDs). To date, there has been a lack of research comparing attention in adults with ASD and adults with ADHD. In study 1, 31 adults with ASD and average intellectual function completed self-report measures of ADHD symptoms. These were compared with self-report measures of ADHD symptoms in 38 adults with ADHD and 29 general population controls. In study 2, 28 adults with a diagnosis of ASD were compared with an age- and intelligence quotient-matched sample of 28 adults with ADHD across a range of measures of attention. Study 1 showed that 36.7% of adults with ASD met Diagnostic and Statistical Manual-IV criteria for current ADHD "caseness" (Barkley Current self-report scores questionnaire). Those with a diagnosis of pervasive developmental disorder-not otherwise specified were most likely to describe ADHD symptoms. The ASD group differed significantly from both the ADHD and control groups on total and individual symptom self-report scores. On neuropsychological testing, adults with ASD and ADHD showed comparable performance on tests of selective attention. Significant group differences were seen on measures of attentional switching; adults with ADHD were significantly faster and more inaccurate, and individuals with Asperger\'s syndrome showed a significantly slower and more accurate response style. Self-reported rates of ADHD among adults with ASD are significantly higher than in the general adult population and may be underdiagnosed. Adults with ASD have attentional difficulties on some neuropsychological measures.'
    #             ],
    #             "ground_truth": "The prevalence of attention deficit hyperactivity disorder (ADHD) in adults with autism spectrum disorders (ASDs) is significantly higher than in the general adult population.",
    #             "evolution_type": "simple",
    #             "episode_done": True,
    #         },
    #     ]
    # )

    print(f"Dataset prepared with {len(dataset)} elements")
    print(dataset.to_dict())

    # TODO: uncomment when ready, this is a safety measure
    # evaluate_retrieval(dataset)
    print("Retrieval Ragas Evaluation completed")
