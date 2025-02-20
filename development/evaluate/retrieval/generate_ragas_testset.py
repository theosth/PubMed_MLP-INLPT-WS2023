import sys
from pathlib import Path
import random

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from development.commons import env
from development.retrieve.opensearch_connector import (
    execute_query,
    create_single_match_BM25_query,
    extract_hits_from_response,
    extract_source_from_hits,
)
from development.evaluate.retrieval.local_ragas_testset_generator import (
    get_local_TestsetGenerator,
)
import os
import json
from dotenv import load_dotenv, find_dotenv
from typing import Optional
from pydantic import BaseModel, RootModel
from pydantic.json import pydantic_encoder

# load the environment variables
_ = load_dotenv(find_dotenv(raise_error_if_not_found=True))


from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from ragas import evaluate
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context, conditional


def extract_metadata_abstracts(record: dict, metadata: dict):
    # add all but the abstract to the metadata
    metadata.update({k: v for k, v in record.items() if k != "abstract"})
    # remove 'souce' and 'seq_num' from metadata
    metadata.pop("source", None)
    metadata.pop("seq_num", None)
    return metadata


def get_abstract_documents(amount: int = 10) -> list[Document]:
    data = JSONLoader(
        file_path=env.ABSTRACTS_DATASET_PATH,
        jq_schema=".documents[]",
        content_key="abstract",
        metadata_func=extract_metadata_abstracts,
    ).load()
    return data[:amount]


def extract_metadata_abstract_fragments(record: dict, metadata: dict):
    # add all but the abstract to the metadata
    metadata.update({k: v for k, v in record.items() if k != "abstract"})
    # set 'source' to 'pmid' and 'seq_num' to 'fragment_id'
    metadata.pop("source", None)
    metadata.pop("seq_num", None)
    # set the file name to the pmid; ragas uses this to identify the document
    metadata["file_name"] = record["pmid"]
    return metadata


def get_abstract_fragments(amount: int = 10) -> list[Document]:
    data = JSONLoader(
        file_path=env.ABSTRACT_FRAGMENT_DATASET_PATH,
        jq_schema=".documents[]",
        content_key="abstract_fragment",
        metadata_func=extract_metadata_abstract_fragments,
    ).load()
    if amount is None:
        return datagenerate_with_langchain_docs

    # shuffle the data and return the first 'amount' of documents
    random.shuffle(data)
    return data[:amount]


def generate_testset(
    generator: TestsetGenerator,
    data: list[Document],
    amount: int = 10,
    file_path: str = env.RAGAS_TESTSET_PATH,
):
    # first check if the file path is valid with a sample json
    try:
        with open(file_path, "w") as f:
            json.dump({"message": "Testset filepath is valid"}, f, indent=2)
    except Exception as e:
        print(f"Error: {e}")
        return
    print("Testset filepath is valid")

    testset = generator.generate_with_langchain_docs(
        documents=data,
        test_size=amount,
        distributions={simple: 0.5, multi_context: 0.25, reasoning: 0.25},
        with_debugging_logs=True,
        is_async=False,
        raise_exceptions=False,
    )
    return testset.to_pandas().to_json(file_path, orient="records", indent=2)


class RagasRefinedDatasetEntry(BaseModel):
    question: str
    contexts: list[str]
    ground_truth: str
    evolution_type: str
    episode_done: bool
    pmids: Optional[list[str]] = None
    fragment_ids: Optional[list[int]] = None
    ids: Optional[list[str]] = None

class OwnDatasetEntry(BaseModel):
    question: str
    pmid: str
    fragment_id: int
    id: str
    question_type: str


def convert_ragas_dataset_to_own_dataset(
    ragas_dataset: list[RagasRefinedDatasetEntry],
    save_to_file: bool = False,
    file_path: str = env.RETRIEVAL_TESTSET_FROM_RAGAS_TESTSET_PATH,
) -> list[OwnDatasetEntry]:
    own_dataset: list[OwnDatasetEntry] = []
    for entry in ragas_dataset:
        if len(entry.contexts) > 1:
            raise ValueError("Only one context per question is expected")
        if len(entry.pmids) > 1:
            raise ValueError("Only one pmid per question is expected")
        if len(entry.fragment_ids) > 1:
            raise ValueError("Only one fragment_id per question is expected")
        if len(entry.ids) > 1:
            raise ValueError("Only one id per question is expected")
        own_dataset.append(
            OwnDatasetEntry(
                question=entry.question,
                pmid=entry.pmids[0],
                fragment_id=entry.fragment_ids[0],
                id=entry.ids[0],
                question_type=entry.evolution_type,
            )
        )

    if save_to_file:
        with open(file_path, "w") as f:
            own_dataset_json = json.dumps(
                own_dataset, indent=2, default=pydantic_encoder
            )
            # print(file_path)
            # encase in {questions: [own_dataset_json]}
            own_dataset_json = f'{{"questions": {own_dataset_json}}}'
            f.write(own_dataset_json)

    return own_dataset

def load_ragas_testset(file_path: str = env.RAGAS_UDATED_TESTSET_PATH) -> list[RagasRefinedDatasetEntry]:
    json_data = None
    with open(file_path, "r") as f:
        json_data = json.load(f)
    return [RagasRefinedDatasetEntry(**entry) for entry in json_data]

def get_matching_abstracts_from_opensearch(
    testset_file_path: str = env.RAGAS_TESTSET_PATH,
    updated_testset_file_path: str = env.RAGAS_UDATED_TESTSET_PATH,
    overwrite_updated_testset: bool = False,
) -> list[dict]:
    # load the testset
    with open(testset_file_path, "r") as f:
        testset = json.load(f)

    # print(testset[0])
    # get the abstracts from opensearch
    for item in testset:
        pmids = []
        fragment_ids = []
        ids = []
        for context in item["contexts"]:
            query = create_single_match_BM25_query(context, "abstract_fragment")
            response = execute_query(
                query=query,
                index=env.OPENSEARCH_ABSTRACT_FRAGMENT_INDEX,
                source_includes=[
                    "id",
                    "fragment_id",
                    "title",
                    "pmid",
                    "fragment_abstract",
                ],
                size=1,
            )
            query_data = extract_source_from_hits(extract_hits_from_response(response))
            pmids.append(query_data[0]["pmid"])
            fragment_ids.append(query_data[0]["fragment_id"])
            ids.append(query_data[0]["id"])
        item["pmids"] = pmids
        item["fragment_ids"] = fragment_ids
        item["ids"] = ids

    if overwrite_updated_testset:
        with open(updated_testset_file_path, "w") as f:
            json.dump(testset, f, indent=2)

    return testset


if __name__ == "__main__":
    # abstracts = get_abstract_documents(amount=1000)
    abstract_fragments = get_abstract_fragments(amount=1000)
    print("Abstract fragments loaded successfully")
    # choose a testset generator:
    # ! local one (currently not functional)
    # generator = get_local_TestsetGenerator()

    # openai - generator:
    # ! execution costs money
    # # create a testset generator
    generator = TestsetGenerator.with_openai(
        generator_llm="gpt-3.5-turbo-16k",
        embeddings="text-embedding-ada-002",
        critic_llm="gpt-3.5-turbo-16k",
    )

    generate_testset(generator, abstract_fragments, amount=100)
    print("Testset generated successfully")
    # print(abstract_fragments[0])

    # get_matching_abstracts_from_opensearch(overwrite_updated_testset=True)

    # convert_ragas_dataset_to_own_dataset(
    #     ragas_dataset=load_ragas_testset(),
    #     save_to_file=True,
    # )