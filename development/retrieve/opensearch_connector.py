import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from development.commons.utils import get_model_id, get_opensearch_client
from development.commons import env

from sentence_transformers import SentenceTransformer

MODEL = SentenceTransformer(env.EMBEDDING_MODEL_NAME)
CLIENT = get_opensearch_client()


def execute_query(
    query,
    index: str = "abstracts",
    source_includes: list[str] = ["_id", "fragment_id"],
    size: int = 5,
    extra_params: dict[str, any] = None,
):
    """
    Execute a generic query on the OpenSearch index.
    :param query: The query to execute.
    :param index: The index to execute the query on.
    :param source_includes: The fields to include in the response.
    :param size: The number of results to return.
    :param extra_params: Additional parameters for OpenSearch query execution.
    :return: The response from OpenSearch.
    """
    query_body = {"size": size, "query": query}

    # Parse additional parameters for the request
    request_params = {}
    if extra_params:
        request_params.update(extra_params)

    return CLIENT.search(
        body=query_body,
        index=index,
        _source_includes=source_includes,
        params=request_params,
    )


def execute_hybrid_query(
    query,
    pipeline_weight: float = 0.0,
    index: str = "abstracts",
    source_includes: list[str] = ["_id", "fragment_id", "pmid"],
    size: int = 5,
    query_name_prefix: str = "hybrid_search_pipeline_weight_",
):
    """
    Execute a hybrid query on the OpenSearch index. The hybrid query combines BM25 and neural search.
    It uses the specified pipeline weight to determine the balance between the two.
    The query is executed with a search pipeline whose name is parsed from the `query_name_prefix` and `pipeline_weight` parameters.
    **IMPORTANT: This pipeline must already exist in OpenSearch**
    :param query: The query to execute.
    :param pipeline_weight: The weight of the neural part of the hybrid query. Must be between 0 and 1.
    :param index: The index to execute the query on.
    :param source_includes: The fields to include in the response.
    :param size: The number of results to return.
    :param query_name_prefix: The prefix to use for the query name.
    :return: The response from OpenSearch.
    """
    if pipeline_weight < 0.0 or pipeline_weight > 1.0:
        raise ValueError("Pipeline weight must be between 0 and 1.")

    # Define the pipeline ID based on the weight
    pipeline_id = f"{query_name_prefix}{pipeline_weight:.2f}"
    extra_params = {"search_pipeline": pipeline_id}

    # Use the generic execute_query function
    return execute_query(
        query=query,
        index=index,
        source_includes=source_includes,
        size=size,
        extra_params=extra_params,
    )


def extract_hits_from_response(response: dict[str, any]):
    """
    Post-process the response from OpenSearch.
    If no hits are found, an empty list is returned.
    :param response: The response from OpenSearch.
    :return: The post-processed response.
    """
    try:
        hits = response["hits"]["hits"]
    except KeyError:
        return []

    return hits


def extract_source_from_hits(hits: list[dict[str, any]]):
    """
    Extract the source fields from a list of hits.
    :param hits: The list of hits from OpenSearch.
    :return: A list of source fields.
    """
    return [hit["_source"] for hit in hits]


def extract_top_k_unique_pmids_from_response(response: dict[str, any], k: int = None):
    """
    Extract the top k unique pmids from the response in the order they appear.
    :param response: The response from OpenSearch.
    :param k: The number of pmids to return. If None, all pmids are returned.
    :return: A list of pmids.
    """
    seen_pmids = set()  # Keep track of seen pmids
    unique_pmids = []  # Store the unique pmids in order
    for hit in response["hits"]["hits"]:
        pmid = hit["_source"]["pmid"]
        if pmid not in seen_pmids:
            unique_pmids.append(pmid)
            seen_pmids.add(pmid)
            if k and len(unique_pmids) == k:
                break
    return unique_pmids


def create_term_query(match_value: str, match_key: str = "pmid"):
    return {"term": {match_key: {"value": match_value}}}


def create_single_match_BM25_query(
    query_text: str, match_on: str = "abstract_fragment"
):
    return {"match": {match_on: {"query": query_text}}}


def create_multi_match_BM25_query(
    query_text: str,
    match_on_fields: list[str] = ["abstract_fragment", "title", "keyword_list"],
):
    return {"multi_match": {"query": query_text, "fields": match_on_fields}}


def create_knn_query(query_text: str, k: int = 10):
    return {
        "knn": {
            "abstract_fragment_embedding": {
                "vector": MODEL.encode(query_text).tolist(),
                "k": k,
            }
        }
    }


def create_hybrid_query(
    query_text: str,
    match_on_fields: list[str] = ["abstract_fragment", "title", "keyword_list"],
    knn_k: int = 10,
):
    return {
        "hybrid": {
            "queries": [
                create_knn_query(query_text, k=knn_k),
                create_multi_match_BM25_query(query_text, match_on_fields),
            ],
        }
    }


# How to Use:
if __name__ == "__main__":
    print("Hybrid Query:")
    size = 10
    # How to use Hybrid Query
    hybrid_query = create_hybrid_query(
        query_text="artificial intelligence",
        match_on_fields=["abstract_fragment", "title", "keyword_list"],
        knn_k=size,
    )

    response_hybrid = execute_hybrid_query(
        query=hybrid_query,
        pipeline_weight=0.5,
        size=size,
        source_includes=["_id", "fragment_id", "title", "pmid"],
    )
    # print(json.dumps(response, indent=2))
    hits_hybrid = extract_hits_from_response(response_hybrid)
    print(json.dumps(hits_hybrid, indent=2))

    print("\n Top 3 unique PMIDs:")
    # extract the top 3 unique pmids from the response
    unique_pmids = extract_top_k_unique_pmids_from_response(response_hybrid, k=3)
    print(unique_pmids)

    print("\n\nTerms Query:")

    # How to use term query
    term_query = create_term_query(match_key="pmid", match_value="32083959")
    response_term = execute_query(
        query=term_query,
        index="abstracts",
        source_includes=["_id", "fragment_id", "title", "pmid"],
        size=10,
    )
    # its possible to only get the source fields (title, pmid, etc.) from the hits
    hits_term = extract_source_from_hits(extract_hits_from_response(response_term))
    print(json.dumps(hits_term, indent=2))
