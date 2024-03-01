import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from pydantic import BaseModel
from typing import Optional, List, Union, Literal
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain.retrievers import EnsembleRetriever


from development.retrieve.opensearch_connector import (
    create_knn_query,
    create_multi_match_BM25_query,
    create_hybrid_query,
    execute_hybrid_query,
    create_term_query,
    execute_query,
    extract_hits_from_response,
    extract_source_from_hits,
)

import development.commons.env as env
from development.commons.utils import get_opensearch_client
from development.retrieve.self_query import get_filters
import development.retrieve.confidence_score as confidence_score


CLIENT = get_opensearch_client()

# Hybrid Query parameters
NEURAL_WEIGHT = 0.5
MATCH_ON_FIELDS = ["abstract_fragment", "title", "keyword_list"]
ABSTRACT_INDEX = env.OPENSEARCH_ABSTRACT_INDEX
ABSTRACT_FRAGMENT_INDEX = env.OPENSEARCH_ABSTRACT_FRAGMENT_INDEX
MAX_FRAGMENTS_PER_ABSTRACT = 8


class AbstractOpenSearch(BaseModel):
    ingested_at: str
    publication_date: str
    abstract: str
    pmid: str
    title: str
    author_list: list[str]
    doi: str
    keyword_list: list[str]

    # not a part of the original response:
    confidence: Optional[Union[str, int]] = None
    filters: Optional[dict] = None


class AbstractFragmentOpenSearch(BaseModel):
    abstract_fragment: str
    pmid: str
    title: str
    author_list: list[str]
    keyword_list: list[str]
    number_of_fragments: int
    fragment_id: int
    ingested_at: str
    publication_date: str
    id: str
    abstract_fragment_embedding: list[float]
    doi: str

    # not a part of the original response:
    confidence: Optional[Union[str, int]] = None
    filters: Optional[dict] = None


def retrieve_abstract_fragments(
    question: str,
    amount: int = 3,
    self_query_retrieval: bool = False,
    strategy: Literal[
        "reciprocal_rank_fusion", "opensearch_hybrid"
    ] = "reciprocal_rank_fusion",
) -> list[AbstractFragmentOpenSearch]:
    """
    Retrieve a list of abstract fragments relevant to the given question.
    :param question: The question to retrieve abstract fragments for.
    :param amount: The number of abstract fragments to retrieve.
    :param self_query_retrieval: Whether to retrieve fragments using self-querying.
    :param strategy: Select by which strategy the hybrid search should work
    :return: A list of AbstractFragmentOpenSearch.
    """

    # Extract query filters for self-query retrieval
    filters = None
    if self_query_retrieval:
        filters = get_filters(question, remove_dot_metadata_from_keys=True)

    if strategy == "opensearch_hybrid":
        abstract_fragments = _retrieve_abstract_fragments_opensearch_hybrid_query(
            question, filters, amount, NEURAL_WEIGHT
        )
    elif strategy == "reciprocal_rank_fusion":
        abstract_fragments = _retrieve_abstract_fragments_reciprocal_rank_fusion(
            question, filters, amount, NEURAL_WEIGHT
        )
    else:
        raise ValueError(f"Invalid strategy: {strategy}")

    for fragment in abstract_fragments:
        fragment.filters = filters

    return abstract_fragments


def _retrieve_abstract_fragments_opensearch_hybrid_query(
    question, filters, amount, weight
) -> list[AbstractFragmentOpenSearch]:
    """
    Retrieve a list of abstract fragments relevant to the given question utilizing the opensearch hybrid query.
    :param question: The question to retrieve abstract fragments for.
    :param filters: Restrict the query to documents that fulfill the filter criteria
    :param amount: The number of abstract fragments to retrieve.
    :param weight: The weight of the semantic part of the hybrid query. Must be between 0 and 1.
    :return: A list of AbstractFragmentOpenSearch.
    """
    query = create_hybrid_query(
        query_text=question, match_on_fields=MATCH_ON_FIELDS, knn_k=amount
    )

    # Send the query to OpenSearch via API
    fragment_response = execute_hybrid_query(
        query=query,
        pipeline_weight=weight,
        index=ABSTRACT_FRAGMENT_INDEX,
        size=amount,
        filter=filters,
    )
    abstract_fragment_data = extract_source_from_hits(
        extract_hits_from_response(fragment_response)
    )
    return [AbstractFragmentOpenSearch(**data) for data in abstract_fragment_data]


def _retrieve_abstract_fragments_reciprocal_rank_fusion(
    question, filters, amount, weight
) -> list[AbstractFragmentOpenSearch]:
    """
    Retrieve a list of abstract fragments relevant to the given question utilizing a custom
    hybrid query implementation that combines the ranks with reciprocal rank fusion.
    :param question: The question to retrieve abstract fragments for.
    :param filters: Restrict the query to documents that fulfill the filter criteria
    :param amount: The number of abstract fragments to retrieve.
    :param weight: The weight of the semantic part of the hybrid query. Must be between 0 and 1.
    :return: A list of AbstractFragmentOpenSearch.
    """
    knn_query = create_knn_query(query_text=question, k=amount)
    multi_match_query = create_multi_match_BM25_query(
        query_text=question, match_on_fields=MATCH_ON_FIELDS
    )
    queries = [knn_query, multi_match_query]

    dummy_retriever = (
        CustomOpensearchAbstractFragmentRetriever()
    )  # This retriever is NOT used. It is only there because ensamle retriever needs a list of retrievers.
    ensemble_retriever = EnsembleRetriever(
        weights=[weight, 1 - weight], retrievers=[dummy_retriever, dummy_retriever]
    )

    fragments_list = []
    for query in queries:
        # Send the query to OpenSearch via API
        fragment_response = execute_query(
            query=query,
            index=ABSTRACT_FRAGMENT_INDEX,
            size=amount,
            filter=filters,
        )
        abstract_fragment_data = extract_source_from_hits(
            extract_hits_from_response(fragment_response)
        )
        fragments = [
            AbstractFragmentOpenSearch(**data) for data in abstract_fragment_data
        ]
        fragments = convert_abstract_fragments_to_langchain_documents(fragments)
        fragments_list.append(fragments)

    fragments = ensemble_retriever.weighted_reciprocal_rank(fragments_list)

    return convert_langchain_documents_to_abstract_fragments(fragments)


def retrieve_abstracts_from_pmids(pmids: list[str]) -> list[AbstractOpenSearch]:
    """
    Retrieve a list of abstracts for a given list of pmids from OpenSearch
    :param pmids: A list of pmids.
    :return: A list of Abstracts.
    """

    # Construct term queries to retrieve each abstract
    term_queries = [
        create_term_query(match_key="pmid", match_value=pmid) for pmid in pmids
    ]

    # Retrieve each abstract individually
    documents: list[AbstractOpenSearch] = []
    for term_query in term_queries:
        # Execute exact query
        response = execute_query(
            query=term_query,
            index=ABSTRACT_INDEX,
            size=1,
        )

        # Extract payload
        hit = extract_hits_from_response(response)
        data = extract_source_from_hits(hit)[0]

        # Assert valid payload
        if len(data) < 0:
            TypeError(f"Could not retrieve document for pmid: {fragment_pmids[index]}")

        # Parse to document structure
        documents.append(AbstractOpenSearch(**data))
    return documents


def convert_abstracts_to_langchain_documents(
    documents: list[AbstractOpenSearch],
) -> list[Document]:
    """
    Convert a list of AbstractOpenSearch objects to a list of langchain Document objects.
    :param documents: A list of AbstractOpenSearch objects.
    :return: A list of langchain compatible Document objects.
    """
    doc_list = []
    for doc in documents:
        metadata = doc.model_dump()
        abstract = metadata.pop("abstract")
        doc_list.append(Document(page_content=abstract, metadata=metadata))
    return doc_list


def convert_abstract_fragments_to_langchain_documents(
    documents: list[AbstractFragmentOpenSearch],
) -> list[Document]:
    """
    Convert a list of AbstractFragmentOpenSearch objects to a list of langchain Document objects.
    :param documents: A list of AbstractFragmentOpenSearch objects.
    :return: A list of langchain compatible Document objects.
    """
    doc_list = []
    for doc in documents:
        metadata = doc.model_dump()
        abstract_fragment = metadata.pop("abstract_fragment")
        doc_list.append(Document(page_content=abstract_fragment, metadata=metadata))
    return doc_list


def convert_langchain_documents_to_abstracts(
    documents: list[Document],
) -> list[AbstractOpenSearch]:
    """
    Convert a list of Document objects to a list of AbstractOpenSearch objects.
    :param documents: A list of Document objects.
    :return: A list of AbstractOpenSearch objects.
    """
    doc_list = []
    for doc in documents:
        metadata = doc.metadata
        abstract = doc.page_content
        metadata["abstract"] = abstract
        doc_list.append(AbstractOpenSearch(**metadata))
    return doc_list


def convert_langchain_documents_to_abstract_fragments(
    documents: list[Document],
) -> list[AbstractFragmentOpenSearch]:
    """
    Convert a list of Document objects to a list of AbstractFragmentOpenSearch objects.
    :param documents: A list of Document objects.
    :return: A list of AbstractFragmentOpenSearch objects.
    """
    doc_list = []
    for doc in documents:
        metadata = doc.metadata
        abstract_fragment = doc.page_content
        metadata["abstract_fragment"] = abstract_fragment
        doc_list.append(AbstractFragmentOpenSearch(**metadata))
    return doc_list


class CustomOpensearchAbstractFragmentRetriever(BaseRetriever):
    """
    A custom langchain retriever that retrieves relevant abstract fragments from an OpenSearch index.
    """

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
        amount: int = 3,
        calculate_confidence: bool = True,
        self_query_retrieval: bool = False,
    ) -> List[Document]:

        abstract_fragments = retrieve_abstract_fragments(
            query, amount, self_query_retrieval
        )

        # Compute confidence ratings for each fragment
        if calculate_confidence:
            confidence_ratings = confidence_score.compute_confidence_ratings(
                query=query,
                texts=[fragment.abstract_fragment for fragment in abstract_fragments],
            )
            # Assign confidence ratings to fragments
            for index, fragment in enumerate(abstract_fragments):
                fragment.confidence = confidence_ratings[index]

        return convert_abstract_fragments_to_langchain_documents(abstract_fragments)


def extract_top_k_unique_abstract_fragments(
    abstract_fragments: list[AbstractFragmentOpenSearch], k: int = None
):
    unique_pmids = set()
    top_k_fragments: list[AbstractFragmentOpenSearch] = []

    for fragment in abstract_fragments:
        if fragment.pmid not in unique_pmids:
            # Determine Uniqueness
            unique_pmids.add(fragment.pmid)
            top_k_fragments.append(fragment)
            # Stop searching if k unique are found
            if k and len(unique_pmids) == k:
                break
    return top_k_fragments


class CustomOpensearchAbstractRetriever(BaseRetriever):
    """
    A custom langchain retriever that retrieves relevant abstracts from an OpenSearch index.
    """

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
        amount: int = 3,
        calculate_confidence: bool = True,
        self_query_retrieval: bool = False,
    ) -> List[Document]:

        # Retrieve abstract fragments
        abstract_fragments = retrieve_abstract_fragments(
            query, amount * MAX_FRAGMENTS_PER_ABSTRACT, self_query_retrieval
        )

        # Filter out duplicate abstracts
        top_k_unique_abstract_fragments = extract_top_k_unique_abstract_fragments(
            abstract_fragments=abstract_fragments, k=amount
        )
        unique_pmids = [fragment.pmid for fragment in top_k_unique_abstract_fragments]

        # Retrieve 'amount' abstracts from obtained pmids
        abstracts = retrieve_abstracts_from_pmids(unique_pmids)

        if calculate_confidence:
            confidence_ratings = confidence_score.compute_confidence_ratings(
                query=query,
                texts=[
                    fragment.abstract_fragment
                    for fragment in top_k_unique_abstract_fragments
                ],
            )

            # Assign confidence ratings to abstracts
            for abstract, confidence in zip(abstracts, confidence_ratings):
                abstract.confidence = confidence

        # Transmit filters from fragments to corresponding abstracts
        for abstract, fragment in zip(abstracts, top_k_unique_abstract_fragments):
            abstract.filters = fragment.filters

        return convert_abstracts_to_langchain_documents(abstracts)


#############################
#       Example Usage       #
#############################
if __name__ == "__main__":
    question = "What is the impact of COVID-19 on mental health?"
    amount = 3

    # Test abstract fragment retriever
    abstract_fragment_retriever = CustomOpensearchAbstractFragmentRetriever()
    abstract_fragments = abstract_fragment_retriever.get_relevant_documents(
        question, amount=amount, calculate_confidence=True, self_query_retrieval=False
    )

    # Test abstract retriever
    abstract_retriever = CustomOpensearchAbstractRetriever()
    abstracts = abstract_retriever.get_relevant_documents(
        question, amount=amount, calculate_confidence=True, self_query_retrieval=False
    )

    print("Abstract Fragments:\n")
    print(abstract_fragments)
    print("\n\n")
    print("Abstracts:\n")
    print(abstracts)
