import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
import development.commons.env as env

from pydantic import BaseModel
from typing import Optional, List
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document


from development.retrieve.opensearch_connector import (
    create_hybrid_query,
    execute_hybrid_query,
    create_term_query,
    execute_query,
    extract_hits_from_response,
    extract_source_from_hits,
    extract_top_k_unique_pmids_from_response,
)
import development.commons.env as env
from development.commons.utils import get_opensearch_client
from development.retrieve.self_query import get_filters


CLIENT = get_opensearch_client()

# Hybrid Query parameters
NEURAL_WEIGHT = 0.5
MATCH_ON_FIELDS = ["abstract_fragment", "title", "keyword_list"]
ABSTRACT_INDEX = env.OPENSEARCH_ABSTRACT_INDEX
ABSTRACT_FRAGMENT_INDEX = env.OPENSEARCH_ABSTRACT_FRAGMENT_INDEX
MAX_FRAGMENTS_PER_ABSTRACT = 20


class DocumentOpenSearch(BaseModel):
    pmid: str
    title: Optional[str] = None
    publication_date: Optional[str] = None
    abstract: str
    author_list: Optional[list[str]] = None
    doi: str
    keyword_list: Optional[list[str]] = None


def retrieve_abstracts(question: str, amount: int = 3) -> list[DocumentOpenSearch]:
    """
    Retrieve a list of abstract documents relevant to the given question.
    :param question: The question to retrieve abstracts for.
    :param amount: The number of abstracts to retrieve.
    :return: A list of Documents.
    """

    filters = get_filters(question, remove_dot_metadata_from_keys=True)

    # Retrieve relevant abstract_fragment pmids
    size = amount * MAX_FRAGMENTS_PER_ABSTRACT
    query = create_hybrid_query(
        query_text=question, match_on_fields=MATCH_ON_FIELDS, knn_k=size
    )
    fragment_response = execute_hybrid_query(
        query=query,
        pipeline_weight=NEURAL_WEIGHT,
        index=ABSTRACT_FRAGMENT_INDEX,
        size=size,
        source_includes=["pmid"],
        filter=filters,
    )
    pmids = extract_top_k_unique_pmids_from_response(fragment_response, amount)

    # Retrieve document abstracts with pmids
    term_queries = [
        create_term_query(match_key="pmid", match_value=pmid) for pmid in pmids
    ]
    documents: list[DocumentOpenSearch] = []
    for index, term_query in enumerate(term_queries):
        response = execute_query(
            query=term_query,
            index=ABSTRACT_INDEX,
            source_includes=[
                "pmid",
                "title",
                "publication_date",
                "abstract",
                "author_list",
                "doi",
                "keyword_list",
            ],
            size=1,
            filter=filters,
        )
        hit = extract_hits_from_response(response)
        data = extract_source_from_hits(hit)[0]
        if len(data) < 0:
            TypeError(f"Could not retrieve document for pmid: {pmids[index]}")
        # print(f"Test: {data}")
        documents.append(DocumentOpenSearch(**data))
    return documents


def convertToDocument(documents: list[DocumentOpenSearch]) -> list[Document]:
    """
    Convert a list of DocumentOpenSearch objects to a list of Document objects.
    :param documents: A list of DocumentOpenSearch objects.
    :return: A list of Document objects.
    """
    doc_list = []
    for doc in documents:
        metadata = doc.dict()
        abstract = metadata.pop('abstract')
        doc_list.append(Document(page_content=abstract, metadata=metadata))
    return doc_list


class CustomOpensearchRetriever(BaseRetriever):
    """
    A custom langchain retriever that retrieves relevant documents from an OpenSearch index.
    """

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
        amount: int = 3,
    ) -> List[Document]:
        return convertToDocument(retrieve_abstracts(query, amount))


#############################
#       Example Usage       #
#############################
if __name__ == "__main__":
    question = "What is the impact of COVID-19 on mental health?"
    amount = 3
    documents_basic = retrieve_abstracts(question, amount)
    print(f"Retrieved {len(documents_basic)} documents for the question: {question}")
    for doc in documents_basic:
        print(doc, "\n\n")
    
    # Test custom retriever
    print("Testing custom retriever:\n")
    documents_custom_retr = CustomOpensearchRetriever().get_relevant_documents(question, amount=amount)
    print(f"Retrieved {len(documents_custom_retr)} documents for the question: {question}")
    for doc in documents_custom_retr:
        print(doc, "\n\n")
