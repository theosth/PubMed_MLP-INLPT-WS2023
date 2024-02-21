import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from development.retrieve.opensearch_connector import (
    execute_hybrid_query,
    create_hybrid_query,
    extract_hits_from_response,
)
import development.commons.env as env

# from 0.0 to 1.0 with 0.05 steps
PIPELINE_WEIGHTS = [i / 20 for i in range(21)]
# INDEX = env.OPENSEARCH_FRAGMENT_INDEX
INDEX = "abstracts"  # TODO! change to the correct index when adjusted in opensearch


# metrics for evaluation
def binary_check(retrieved_document_ids: list, relevant_document_id: str, eval_metric_settings=None) -> int:
    """
    Check if the relevant document is in the retrieved list.
    :param retrieved_document_ids: List of retrieved document IDs.
    :param relevant_document_id: The relevant document ID.
    :return: 1 if the relevant document is retrieved, else 0.
    """
    return int(relevant_document_id in retrieved_document_ids)


def rank_score(retrieved_document_ids: list, relevant_document_id: str, eval_metric_settings=None) -> float:
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
    retrieved_document_ids: list, relevant_document_id: str, k: int
) -> int:
    """
    Check if the relevant document is within the top-k retrieved documents.
    :param retrieved_document_ids: List of retrieved document IDs.
    :param relevant_document_id: The relevant document ID.
    :param k: The cut-off rank (top-k).
    :return: 1 if the relevant document is within the top-k, else 0.
    """
    return int(relevant_document_id in retrieved_document_ids[:k])


def evaluate_pipeline(
    pipeline_weight: float,
    querys: list[dict],
    index: str,
    source_includes: list,
    size: int,
    eval_metric,
    eval_metric_settings=None,
):  
    scores = []
    for query in querys:
        hybrid_query = create_hybrid_query(query["question"])
        response = execute_hybrid_query(
            hybrid_query, pipeline_weight, index, source_includes, size
        )
        hits = extract_hits_from_response(response)
        retrieved_document_ids = [hit["_id"] for hit in hits]
        score = eval_metric(retrieved_document_ids, query["id"], eval_metric_settings)
        scores.append(score)
    return scores


def evaluate_pipelines(
    pipeline_weights: list,
    query: dict,
    index: str,
    source_includes: list,
    size: int,
    eval_metric,
):
    scores = []
    for pipeline_weight in pipeline_weights:
        score = evaluate_pipeline(
            pipeline_weight, query, index, source_includes, size, binary_at_k, {"k": 3}
        )
        scores.append(score)
    return scores

# For testing
question_doc = [
    {
        "question": "Was an artificial intelligence system developed to evaluate the reliability and consistency of sleep scoring among sleep centers?",
        "pmid": "32964831",
        "fragment_id": 0,
        "id": "32964831_0",
        "question_type": "yes/no",
    },
    {
        "question": "Has the advent of artificial intelligence technology led to advancements in the diagnosis and treatment of ophthalmic diseases?",
        "pmid": "37012586",
        "fragment_id": 0,
        "id": "37012586_0",
        "question_type": "yes/no",
    },
    {
        "question": "Is it trained for another system?",
        "pmid": "37172147",
        "fragment_id": 1,
        "id": "37172147_1",
        "question_type": "yes/no",
    },
    {
        "question": "Did the share of research outputs related to the pandemic almost double from 2020 to 2021?",
        "pmid": "37766916",
        "fragment_id": 0,
        "id": "37766916_0",
        "question_type": "yes/no",
    },
    {
        "question": "Is the article with the DOI 10. 1155 / 2022 / 5914561 retracted?",
        "pmid": "37502085",
        "fragment_id": 0,
        "id": "37502085_0",
        "question_type": "yes/no",
    },
    {
        "question": "Did the authors suggest that aspects of general intelligence likely arose in tandem with mechanisms of adaptive motor control that rely on basal ganglia circuitry?",
        "pmid": "29342668",
        "fragment_id": 0,
        "id": "29342668_0",
        "question_type": "yes/no",
    },
    {
        "question": "Do children treated for metopic synostosis show shortcomings in adaptive behavior skills?",
        "pmid": "33565829",
        "fragment_id": 1,
        "id": "33565829_1",
        "question_type": "yes/no",
    },
    {
        "question": "Is nurses' emotional intelligence affected by the complexity of care and type of ward they work in?",
        "pmid": "35094821",
        "fragment_id": 0,
        "id": "35094821_0",
        "question_type": "yes/no",
    },
    {
        "question": "Does the use of autonomous vehicles increase free-time or blur the boundaries between work and non-work time?",
        "pmid": "35400853",
        "fragment_id": 1,
        "id": "35400853_1",
        "question_type": "yes/no",
    },
    {
        "question": "Does assessment of mpas help in diagnosing psychiatric disorders?",
        "pmid": "24782925",
        "fragment_id": 1,
        "id": "24782925_1",
        "question_type": "yes/no",
    },
    {
        "question": "Is there a need to address the ethical and data governance challenges of using digital technology in the operating room?",
        "pmid": "33616543",
        "fragment_id": 0,
        "id": "33616543_0",
        "question_type": "yes/no",
    },
    {
        "question": "Is the attitude of positive psychology considered to be a key factor in the success of workforce rehabilitation processes in Hungary?",
        "pmid": "26294537",
        "fragment_id": 0,
        "id": "26294537_0",
        "question_type": "yes/no",
    },
    {
        "question": "Is thalamus volume significantly correlated with intellectual functioning and influenced by a common genetic factor?",
        "pmid": "24038793",
        "fragment_id": 0,
        "id": "24038793_0",
        "question_type": "yes/no",
    },
]
query_text = "covid-19"
source_includes = ["_id", "fragment_id"]
size = 3

# first test 1
pipeline_weight = 0.5
evaluated_pipeline = evaluate_pipeline(
    pipeline_weight, question_doc, INDEX, source_includes, size, binary_at_k, 3
)
print(evaluated_pipeline)
