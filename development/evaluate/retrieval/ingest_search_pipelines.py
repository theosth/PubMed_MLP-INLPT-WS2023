import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from development.commons.utils import get_opensearch_client

CLIENT = get_opensearch_client()


def create_hybrid_pipeline(
    pipeline_weight: float, pipeline_name_prefix: str = "hybrid_search_pipeline_weight_"
):
    """
    Create a hybrid search pipeline with a specific weight.
    :param pipeline_weight: The weight to assign to the pipeline.
    :param pipeline_name_prefix: The prefix to use for the pipeline name.
    :return: The URL and body for the pipeline.
    """
    pipeline_id = f"{pipeline_name_prefix}{pipeline_weight:.2f}"
    url = f"/_search/pipeline/{pipeline_id}"

    body = json.dumps(
        {
            "description": "Post processor for hybrid search",
            "phase_results_processors": [
                {
                    "normalization-processor": {
                        "normalization": {"technique": "min_max"},
                        "combination": {
                            "technique": "arithmetic_mean",
                            "parameters": {
                                "weights": [pipeline_weight, 1.0 - pipeline_weight]
                            },
                        },
                    }
                }
            ],
        }
    )

    return url, body


def ingest_pipeline(url: str, body: str):
    """
    Ingest a pipeline into OpenSearch.
    :param url: The URL for the pipeline.
    :param body: The body for the pipeline.
    :return: The response from OpenSearch.
    """
    response = CLIENT.http.put(
        url=url,
        body=body,
    )

    return response


def setup_pipelines(pipeline_weights: list = [i / 20 for i in range(21)]):
    """
    Ingest multiple pipelines, required for evaluation into OpenSearch.
    :param pipeline_weights: The weights to assign to the pipelines.
    """

    for pipeline_weight in pipeline_weights:
        url, body = create_hybrid_pipeline(pipeline_weight)
        response = ingest_pipeline(url, body)
        if response['acknowledged'] != True:
          throw(f"Failed to ingest pipeline with weight {pipeline_weight}.")
        else:
          print(f"Ingested pipeline with weight {pipeline_weight}")


if __name__ == "__main__":
    # If this script is run directly, ingest the pipelines
    setup_pipelines()
