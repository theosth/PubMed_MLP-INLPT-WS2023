import json
import sys
import datetime

from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from opensearchpy import helpers
from opensearchpy.exceptions import NotFoundError
from tqdm import tqdm

import development.commons.env as env
import development.commons.utils as utils

# ===== Constants =====
OPENSEARCH_CLIENT = utils.get_opensearch_client()
# ===== Constants =====


def insert_ingest_pipeline():
    ingest_pipeline_id = "abstracts_ingest_pipeline"
    pipeline_body = {
        "description": "Ingest pipeline for abstracts",
        "processors": [
            {
                "set": {
                    "field": "_source.ingested_at",
                    "value": "{{_ingest.timestamp}}"
                }
            }
        ]
    }

    print(f"[{datetime.datetime.now()}] Inserting ingest pipeline into OpenSearch...")
    insert_result = OPENSEARCH_CLIENT.ingest.put_pipeline(
        id=ingest_pipeline_id,
        body=pipeline_body
    )
    print(f"[{datetime.datetime.now()}] Insertion result: {insert_result}")
    return ingest_pipeline_id


def insert_index(ingest_pipeline_id):
    try:
        # Try to delete an already existing index as this facilitates "re-indexing"
        print(f"[{datetime.datetime.now()}] Trying to delete existing index...")
        delete_result = OPENSEARCH_CLIENT.indices.delete(env.OPENSEARCH_ABSTRACT_INDEX)
        print(f"[{datetime.datetime.now()}] Deletion result: {delete_result}")
    except NotFoundError:
        pass

    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "index.knn": True,
            "default_pipeline": ingest_pipeline_id,
            "analysis": {
                "analyzer": {
                    "content_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": []
                    }
                }
            }
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "abstract": {"type": "text"},
                "title": {"type": "text"},  # or keyword?
                "doi": {"type": "keyword"},
                "pmid": {"type": "integer"},  # or keyword?
                "keyword_list": {"type": "keyword"},
                "author_list": {"type": "keyword"},
                "publication_date": {
                    "type": "date",
                    "format": "yyyy-MM-dd|yyyy" # yyyy is required for self-query
                },
                "ingested_at": {"type": "date"}
            }
        }
    }

    print(f"[{datetime.datetime.now()}] Configuring index {env.OPENSEARCH_ABSTRACT_INDEX}...")
    configure_result = OPENSEARCH_CLIENT.indices.create(index=env.OPENSEARCH_ABSTRACT_INDEX, body=settings)
    print(f"[{datetime.datetime.now()}] Configuration result: {configure_result}")


def _bulk_data(documents, index_name):
    for doc in tqdm(documents, file=sys.stdout, total=len(documents)):
        _id: str = doc['pmid']

        yield {
            "_op_type": "create",
            "_index": index_name,
            "_id": _id,
            "_source": doc,
        }


def fill_index():
    # Load Data
    with open(env.ABSTRACTS_DATASET_PATH, 'r') as f:
        documents = json.load(f)['documents']

    # Ingest data using the bulk api
    print(f"[{datetime.datetime.now()}] Inserting data into index {env.OPENSEARCH_ABSTRACT_INDEX}...")
    generator = _bulk_data(documents, env.OPENSEARCH_ABSTRACT_INDEX)
    nb_inserted, errors = helpers.bulk(OPENSEARCH_CLIENT, generator, chunk_size=64, max_retries=2, timeout=60)

    if nb_inserted != len(documents):
        print(f"[{datetime.datetime.now()}] Ingested {nb_inserted}/{len(documents)} fragments.")
        print(f"[{datetime.datetime.now()}] See console output above and below for error details.")
    else:
        print(f"[{datetime.datetime.now()}] Ingested {nb_inserted}/{len(documents)} fragments.")
        print(f"[{datetime.datetime.now()}] {f'Errors: {errors}' if len(errors) > 0 else 'No errors.'}")


if __name__ == "__main__":
    # Configure Ingest Pipeline and Index
    ingest_pipeline_id = insert_ingest_pipeline()
    insert_index(ingest_pipeline_id)

    # Fill Index
    fill_index()
