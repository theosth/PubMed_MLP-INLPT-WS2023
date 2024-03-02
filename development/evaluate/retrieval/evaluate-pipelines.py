import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from development.retrieve.retrieval_wrapper import (
    _retrieve_abstract_fragments_reciprocal_rank_fusion,
)

import development.commons.env as env
from development.retrieve.opensearch_connector import (
    execute_hybrid_query,
    create_hybrid_query,
    extract_hits_from_response,
)
import ijson
from pydantic import BaseModel, FilePath
from typing import Callable, Literal
import pandas as pd
from tqdm import tqdm
import time


class Query(BaseModel):
    question: str
    pmid: str
    fragment_id: int
    id: str
    question_type: str


def read_questions_from_json(
    file_path: FilePath, num_lines: int, max_questions: int = None
):
    """
    Read a specified number of questions at a time from a JSON file, with an optional limit on the total number of questions.
    :param file_path: The path to the JSON file.
    :param num_lines: The number of questions to read at a time.
    :param max_questions: The maximum number of questions to process (optional).
    :yield: A list of questions.
    """
    with open(file_path, "rb") as file:
        objects = ijson.items(file, "questions.item")
        buffer = []
        questions_yielded = 0

        for question in objects:
            if max_questions is not None and questions_yielded >= max_questions:
                break  # Stop reading if the maximum number of questions has been reached

            buffer.append(question)
            if len(buffer) == num_lines:
                yield buffer
                questions_yielded += len(buffer)
                buffer = []

        if buffer and (max_questions is None or questions_yielded < max_questions):
            yield buffer  # Yield any remaining questions in the buffer


# metrics for evaluation
def binary_check(
    retrieved_document_ids: list[str],
    relevant_document_id: str,
    eval_metric_settings=None,
) -> int:
    """
    Check if the relevant document is in the retrieved list.
    :param retrieved_document_ids: List of retrieved document IDs.
    :param relevant_document_id: The relevant document ID.
    :return: 1 if the relevant document is retrieved, else 0.
    """
    return int(relevant_document_id in retrieved_document_ids)


def rank_score(
    retrieved_document_ids: list[str],
    relevant_document_id: str,
    eval_metric_settings=None,
) -> float:
    """
    Compute the  rank of the relevant document in the retrieved list.
    :param retrieved_document_ids: List of retrieved document IDs.
    :param relevant_document_id: The relevant document ID.
    :return: Higher score if document is shown earlier in the list. 0 if not found.
    """
    try:
        rank = retrieved_document_ids.index(relevant_document_id) + 1
        return 1 / rank
    except ValueError:
        return 0


def binary_at_k(
    retrieved_document_ids: list[str],
    relevant_document_id: str,
    eval_metric_settings: dict[str, any],
) -> int:
    """
    Check if the relevant document is within the top-k retrieved documents.
    :param retrieved_document_ids: List of retrieved document IDs.
    :param relevant_document_id: The relevant document ID.
    :param eval_metric_settings: A dictionary containing settings for the evaluation metric.
        The settings should include the value of k.
    :return: 1 if the relevant document is within the top-k, else 0.
    """
    if eval_metric_settings is None or "k" not in eval_metric_settings:
        raise ValueError("Settings for k must be provided.")
    k = eval_metric_settings["k"]
    return int(relevant_document_id in retrieved_document_ids[:k])


def evaluate_pipeline(
    pipeline_weight: float,
    queries: list[Query],
    index: str,
    source_includes: list[str],
    size: int,
    eval_metrics: list[Callable[[list[str], str, dict[str, any]], float]],
    eval_metric_settings: list[dict[str, any]] = None,
    strategy: Literal[
        "reciprocal_rank_fusion", "opensearch_hybrid"
    ] = "opensearch_hybrid",
) -> list[dict[str, float]]:
    """
    Evaluate a set of queries against a search pipeline using multiple evaluation metrics.

    This function executes a search query for each query in the provided list using a hybrid search by neural-weight.
    It then evaluates the search results against each of the specified evaluation metrics
    to generate a score for each query, under each metric.

    :param pipeline_weight: The weight to be applied to the pipeline's hybrid query mechanism.
    :param queries: A list of Query objects, where each Query contains information for executing a search.
    :param index: The name of the OpenSearch index to query against.
    :param source_includes: A list of source fields to include in the response from OpenSearch.
    :param size: The number of search results (documents) to retrieve.
    :param eval_metrics: A list of callable evaluation metrics. Each metric function should accept a list of
        document IDs (as strings), the relevant document ID (as a string), and a settings dictionary,
        returning a float score.
    :param eval_metric_settings: A list of dictionaries containing settings for each evaluation metric.
        Each dictionary in this list corresponds to the respective metric in `eval_metrics`.
        If None, an empty dictionary is used for each metric.
    :param strategy: The strategy to use for retrieval. Options are "opensearch_hybrid" and "reciprocal_rank_fusion".
    :return: A list of dictionaries, each representing the scores of a single query across all metrics.
        The keys in each dictionary are the names of the evaluation metrics, and the values are the scores.

    :raises ValueError: If the length of `eval_metrics` does not match the length of `eval_metric_settings`.
    """

    if eval_metric_settings is None:
        # Set default to {} if not provided
        eval_metric_settings = [{} for _ in eval_metrics]

    # Ensure length of settings list matches length of eval_metrics
    if len(eval_metrics) != len(eval_metric_settings):
        raise ValueError("Length of eval_metrics and eval_metric_settings must match.")

    scores = []
    for query in queries:
        retrieved_document_ids = []
        if strategy == "opensearch_hybrid":
            hybrid_query = create_hybrid_query(query.question)
            response = execute_hybrid_query(
                hybrid_query, pipeline_weight, index, source_includes, size
            )
            hits = extract_hits_from_response(response)
            retrieved_document_ids = [hit["_id"] for hit in hits]
        elif strategy == "reciprocal_rank_fusion":
            fragments = _retrieve_abstract_fragments_reciprocal_rank_fusion(
                query.question, None, size, pipeline_weight
            )
            retrieved_document_ids = [fragment.id for fragment in fragments]
        else:
            raise ValueError(f"Invalid strategy: {strategy}")

        # Apply each evaluation metric to the query results
        query_scores = {
            "pipeline_weight": pipeline_weight,
            "query_id": query.id,
            "retrieved_document_ids": retrieved_document_ids,
        }  # Include neural-weight in the results
        for eval_metric, settings in zip(eval_metrics, eval_metric_settings):
            score = eval_metric(retrieved_document_ids, query.id, settings)
            metric_name = eval_metric.__name__  # get the name of the fun
            query_scores[metric_name] = score
        scores.append(query_scores)
    return scores


def main():
    num_lines = 10  # Number of questions to read and evaluate at a time
    max_queries = 1000  # Maximum number of queries to process.

    # Setup for evaluation
    pipeline_weights = [i / 20 for i in range(21)]  # from 0.0 to 1.0 with 0.05 steps
    index = env.OPENSEARCH_ABSTRACT_FRAGMENT_INDEX
    source_includes = ["_id", "fragment_id"]
    size = 10  # Number of search results to retrieve for each query from OpenSearch
    eval_metrics = [binary_at_k, rank_score]  # specify the metrics to use
    k = 3  # specify the value of k for the binary_at_k metric
    eval_metric_settings = [{"k": k}, {}]

    # file_path = env.RETRIEVAL_TESTSET_PATH
    # output_path_a = f"{env.RETRIEVAL_RESULT_FOLDER_PATH}retrieval_result_scores_s{size}_k{k}_opensearch_hybrid.csv"
    # output_path_b = f"{env.RETRIEVAL_RESULT_FOLDER_PATH}retrieval_result_scores_s{size}_k{k}_rrf.csv"
    
    # For Ragas testset
    file_path = env.RETRIEVAL_TESTSET_FROM_RAGAS_TESTSET_PATH
    output_path_a = f"{env.RETRIEVAL_RESULT_FOLDER_PATH}retrieval_result_scores_s{size}_k{k}_opensearch_hybrid_ragas.csv"
    output_path_b = f"{env.RETRIEVAL_RESULT_FOLDER_PATH}retrieval_result_scores_s{size}_k{k}_rrf_ragas.csv"
    
    first_write = True  # Flag to indicate if header should be written

    # Calculate total number of queries to do for tqdm (assuming each batch is num_lines)
    total_queries_to_process = min(
        max_queries // num_lines, (max_queries + num_lines - 1) // num_lines
    )

    # Process questions in batches with tqdm for progress tracking
    for questions_batch in tqdm(
        read_questions_from_json(file_path, num_lines, max_queries),
        total=total_queries_to_process,
    ):
        queries = [Query(**question) for question in questions_batch]
        for pipeline_weight in pipeline_weights:
            # if an error occours the program will wait 5 seconds and try again
            # -> this helps to avoid connection errors
            # -> also if OpenSearch draws max HEAP memory,
            # this will help to avoid the error because it will wait for GC
            while True:
                try:
                    results_opensearch_hybrid = evaluate_pipeline(
                        pipeline_weight,
                        queries,
                        index,
                        source_includes,
                        size,
                        eval_metrics,
                        eval_metric_settings,
                        "opensearch_hybrid",
                    )
                    results_rrf = evaluate_pipeline(
                        pipeline_weight,
                        queries,
                        index,
                        source_includes,
                        size,
                        eval_metrics,
                        eval_metric_settings,
                        "reciprocal_rank_fusion",
                    )
                    break
                except Exception as e:
                    print(e)
                    time.sleep(2)

            # Convert batch results to DataFrame and write to CSV
            results_df_opensearch_hybrid = pd.DataFrame(results_opensearch_hybrid)
            results_df_rrf = pd.DataFrame(results_rrf)
            results_df_opensearch_hybrid.to_csv(
                output_path_a, mode="a", index=False, header=first_write
            )
            results_df_rrf.to_csv(
                output_path_b, mode="a", index=False, header=first_write
            )

            if first_write:
                first_write = False


if __name__ == "__main__":
    main()
