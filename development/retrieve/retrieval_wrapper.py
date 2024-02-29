import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from pydantic import BaseModel
from typing import Optional, List, Union
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
    extract_top_k_unique_abstract_fragments,
)

import development.commons.env as env
from development.commons.utils import get_opensearch_client
from development.retrieve.self_query import get_filters
import development.retrieve.confidence_score as confidence


CLIENT = get_opensearch_client()

# Hybrid Query parameters
NEURAL_WEIGHT = 0.5
MATCH_ON_FIELDS = ["abstract_fragment", "title", "keyword_list"]
ABSTRACT_INDEX = env.OPENSEARCH_ABSTRACT_INDEX
ABSTRACT_FRAGMENT_INDEX = env.OPENSEARCH_ABSTRACT_FRAGMENT_INDEX
MAX_FRAGMENTS_PER_ABSTRACT = 8


class DocumentOpenSearch(BaseModel):
    pmid: str
    title: Optional[str] = None
    publication_date: Optional[str] = None
    abstract: str
    author_list: Optional[list[str]] = None
    doi: str
    keyword_list: Optional[list[str]] = None
    confidence: Optional[Union[str, int]] = None


def retrieve_abstracts(question: str, amount: int = 3) -> list[DocumentOpenSearch]:
    """
    Retrieve a list of abstract documents relevant to the given question.
    :param question: The question to retrieve abstracts for.
    :param amount: The number of abstracts to retrieve.
    :return: A list of Documents.
    """
    # Extract self-querying filters
    filters = get_filters(question, remove_dot_metadata_from_keys=True)
    size = amount * MAX_FRAGMENTS_PER_ABSTRACT

    # Create and execute hybrid abstract fragment query
    query = create_hybrid_query(
        query_text=question,
        match_on_fields=MATCH_ON_FIELDS,
        knn_k=size
    )

    fragment_response = execute_hybrid_query(
        query=query,
        pipeline_weight=NEURAL_WEIGHT,
        index=ABSTRACT_FRAGMENT_INDEX,
        size=size,
        source_includes=["pmid", "abstract_fragment"],
        filter=filters,
    )

    # Extract first fragments of unique abstracts
    fragment_texts, fragment_pmids = extract_top_k_unique_abstract_fragments(fragment_response, amount)

    # Construct exact abstract query
    term_queries = [
        create_term_query(
            match_key="pmid",
            match_value=pmid)
        for pmid in fragment_pmids
    ]

    # Retrieve each abstract individually
    documents: list[DocumentOpenSearch] = []
    for index, term_query in enumerate(term_queries):
        # Execute exact query
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

        # Extract payload
        hit = extract_hits_from_response(response)
        data = extract_source_from_hits(hit)[0]

        # Assert valid payload
        if len(data) < 0:
            TypeError(f"Could not retrieve document for pmid: {fragment_pmids[index]}")

        # Parse to document structure
        documents.append(DocumentOpenSearch(**data))

    # Compute Confidence
    confidence_ratings = confidence.compute_confidence_ratings(query=question, texts=fragment_texts)
    for index, document in enumerate(documents):
        document.confidence = confidence_ratings[index]

    return documents


def convert_to_document(documents: list[DocumentOpenSearch]) -> list[Document]:
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


def convert_to_document_opensearch(documents: list[Document]) -> list[DocumentOpenSearch]:
    """
    Convert a list of Document objects to a list of DocumentOpenSearch objects.
    :param documents: A list of Document objects.
    :return: A list of DocumentOpenSearch objects.
    """
    doc_list = []
    for doc in documents:
        metadata = doc.metadata
        abstract = doc.page_content
        metadata["abstract"] = abstract
        doc_list.append(DocumentOpenSearch(**metadata))
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
        return convert_to_document(retrieve_abstracts(query, amount))


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
