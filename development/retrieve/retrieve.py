import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from pydantic import BaseModel, validator
from typing import Optional
from development.retrieve.opensearch_connector import (
    create_hybrid_query,
    execute_hybrid_query,
    create_term_query,
    execute_query,
    extract_hits_from_response,
    extract_source_from_hits,
    extract_top_k_unique_pmids_from_response,
)
from development.commons.utils import get_opensearch_client
import development.commons.env as env


CLIENT = get_opensearch_client()

# Hybrid Query parameters
NEURAL_WEIGHT = 0.5
MATCH_ON_FIELDS = ["abstract_fragment", "title", "keyword_list"]
ABSTRACT_INDEX = env.OPENSEARCH_ABSTRACT_INDEX
ABSTRACT_FRAGMENT_INDEX = env.OPENSEARCH_ABSTRACT_FRAGMENT_INDEX
MAX_FRAGMENTS_PER_ABSTRACT = 5  # ! TODO: Check if this is the right value


class Document(BaseModel):
    pmid: str
    title: str
    abstract: str
    author_list: list[str]
    doi: str
    keyword_list: Optional[list[str]] = None


def retrieve_abstracts(question: str, amount: int = 3) -> list[Document]:
    """
    Retrieve a list of abstract documents relevant to the given question.
    :param question: The question to retrieve abstracts for.
    :param amount: The number of abstracts to retrieve.
    :return: A list of Documents.
    """

    # Retrieve relevant abstract_fragment pmids
    size = amount * MAX_FRAGMENTS_PER_ABSTRACT
    query = create_hybrid_query(query_text=question, match_on_fields=MATCH_ON_FIELDS, knn_k=size)
    fragment_response = execute_hybrid_query(
        query=query,
        pipeline_weight=NEURAL_WEIGHT,
        index=ABSTRACT_FRAGMENT_INDEX,
        size=size,
        source_includes=["pmid"],
    )
    pmids = extract_top_k_unique_pmids_from_response(fragment_response, amount)

    # Retrieve document abstracts with pmids
    term_queries = [
        create_term_query(match_key="pmid", match_value=pmid) for pmid in pmids
    ]
    documents: list[Document] = []
    for term_query in term_queries:
        response = execute_query(
            query=term_query,
            index=ABSTRACT_INDEX,
            source_includes=[
                "pmid",
                "title",
                "abstract",
                "author_list",
                "doi",
                "keyword_list",
            ],
            size=1,
        )
        hit = extract_hits_from_response(response)
        data = extract_source_from_hits(hit)[0]
        if len(data) < 0:
            TypeError(f"Could not retrieve document for pmid: {pmid}")
        documents.append(Document(**data))
    return documents


if __name__ == "__main__":
    question = "What is the impact of COVID-19 on mental health?"
    amount = 3
    documents = retrieve_abstracts(question, amount)
    print(f"Retrieved {len(documents)} documents for the question: {question}")
    for doc in documents:
        print(doc)
