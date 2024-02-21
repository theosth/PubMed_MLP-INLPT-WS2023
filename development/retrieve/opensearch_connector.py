import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from commons.utils import get_model_id, get_opensearch_client

CLIENT = get_opensearch_client()


def execute_hybrid_query(
    query,
    pipeline_weight: float = 0.0,
    index="abstracts",
    source_includes=["_id", "fragment_id"],
    size=5,
):
    """
    Execute a query on the OpenSearch index.
    :param query: The query to execute.
    :param pipeline_weight: The weight of the neural-part of the hybrid query. Must be between 0 and 1.
    !IMPORTANT: The pipeline must be registered on the cluster. If you use a hybrid query, the pipeline_id should be specified.
    :param index: The index to execute the query on.
    :param source_includes: The fields to include in the response.
    :param size: The number of results to return.
    :return: The response from OpenSearch.
    """

    PIPELINE_ID_PREFIX = "hybrid_search_pipeline_weight_"
    if pipeline_weight < 0.0 or pipeline_weight > 1.0:
        raise ValueError("Pipeline weight must be between 0 and 1.")

    # convert float to string with 2 decimal places after the dot
    pipeline_id = f"{PIPELINE_ID_PREFIX}{pipeline_weight:.2f}"

    query_body = {"size": size, "query": query}

    return CLIENT.search(
        body=query_body,
        index=index,
        _source_includes=source_includes,
        params={"search_pipeline": pipeline_id},
    )


def extract_hits_from_response(response):
    """
    Post-process the response from OpenSearch.
    If no hits are found, an empty list is returned.
    :param response: The response from OpenSearch.
    :return: The post-processed response.
    """
    try:
        hits = response["hits"]["hits"]
    except KeyError:
        print("No hits found.")
        return []

    return hits


def create_single_match_BM25_query(query_text, match_on="abstract_fragment"):
    return {"match": {match_on: {"query": query_text}}}


def create_multi_match_BM25_query(
    query_text, match_on_fields=["abstract_fragment", "title", "keyword_list"]
):
    return {"multi_match": {"query": query_text, "fields": match_on_fields}}


def create_neural_query(query_text):
    return {
        "neural": {
            "abstract_fragment_embedding": {
                "query_text": query_text,
                "model_id": get_model_id(CLIENT),
            }
        }
    }


def create_hybrid_query(
    query_text, match_on_fields=["abstract_fragment", "title", "keyword_list"]
):
    """
    Create a hybrid query that combines BM25 and neural search.
    """
    return {
        "hybrid": {
            "queries": [
                create_neural_query(query_text),
                create_multi_match_BM25_query(query_text, match_on_fields),
            ],
        }
    }


# How to Use:
if __name__ == "__main__":
    hybrid_query = create_hybrid_query(
        query_text="artificial intelligence",
        match_on_fields=["abstract_fragment", "title", "keyword_list"],
    )

    response = execute_hybrid_query(
        query=hybrid_query,
        pipeline_weight=0.5,
        size=3,
        source_includes=["_id", "fragment_id", "title"],
    )
    # print(json.dumps(response, indent=2))
    hits = extract_hits_from_response(response)
    print(json.dumps(hits, indent=2))
