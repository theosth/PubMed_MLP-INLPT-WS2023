import json
import sys
from datetime import datetime

from opensearch_py_ml.ml_commons import MLCommonClient
from opensearch_py_ml.ml_models import SentenceTransformerModel
from opensearchpy import helpers
from opensearchpy.exceptions import NotFoundError
from tqdm import tqdm

import development.commons.env as env
import development.commons.utils as utils

# ===== Constants =====
INDEX_CONTENT_NAME = "abstract_fragment"
INDEX_CONTENT_EMBEDDING_NAME = "abstract_fragment_embedding"
OPENSEARCH_CLIENT = utils.get_opensearch_client()
# ===== Constants =====


def configure_opensearch_ml_settings():
    # ML Compatability Configuration
    OPENSEARCH_CLIENT.cluster.put_settings(
        {
            "persistent": {
                "plugins": {
                    "ml_commons": {
                        "only_run_on_ml_node": "false",
                        "model_access_control_enabled": "true",
                        "native_memory_threshold": "99",

                        # Required for using custom ML models
                        "allow_registering_model_via_local_file": "true",
                        "allow_registering_model_via_url": "true"
                    }
                }
            }
        }
    )


def initialize_model():
    print(f"[{datetime.datetime.now()}] Retrieving embedding model id...")
    try:
        model_id = utils.get_model_id(OPENSEARCH_CLIENT)
        print(f"[{datetime.datetime.now()}] Embedding model was already registered!")
    except NotFoundError:
        print(f"[{datetime.datetime.now()}] Embedding model is not registered!")
        print(f"[{datetime.datetime.now()}] Setting up embedding model {env.EMBEDDING_MODEL_NAME}", flush=True)
        print(f"[{datetime.datetime.now()}] Downloading...")

        embedding_model = SentenceTransformerModel(
            model_id=env.EMBEDDING_MODEL_NAME,
            folder_path=env.EMBEDDING_MODEL_PATH,
            overwrite=True
        )

        model_save_path = embedding_model.save_as_pt(
            model_id=env.EMBEDDING_MODEL_NAME,
            save_json_folder_path=env.EMBEDDING_MODEL_PATH,
            sentences=["Example sentence"]
        )

        # Parameter "max_length" is contained in the tokenizer config
        model_config_path = embedding_model.make_model_config_json()

        print(f"[{datetime.datetime.now()}] Registering...")
        ml_common_client = MLCommonClient(OPENSEARCH_CLIENT)
        model_id = ml_common_client.register_model(model_save_path, model_config_path, isVerbose=True)
        print(f"[{datetime.datetime.now()}] Registering done!")

    return model_id


def insert_ingest_pipeline(model_id):
    ingest_pipeline_id = "abstract_fragments_ingest_pipeline"
    pipeline_body = {
        "description": "Ingest pipeline for abstract fragments",
        "processors": [
            {
                "set": {
                    "field": "_source.ingested_at",
                    "value": "{{_ingest.timestamp}}"
                }
            },
            {
                "text_embedding": {
                    "model_id": model_id,
                    "field_map": {
                        INDEX_CONTENT_NAME: INDEX_CONTENT_EMBEDDING_NAME
                    }
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
        delete_result = OPENSEARCH_CLIENT.indices.delete(env.OPENSEARCH_ABSTRACT_FRAGMENT_INDEX)
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
                "title": {"type": "text"},  # or keyword?
                "doi": {"type": "keyword"},
                "pmid": {"type": "integer"},  # or keyword? 
                "keyword_list": {"type": "keyword"},
                "author_list": {"type": "keyword"},
                "publication_date": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm:ss"
                },
                "ingested_at": {"type": "date"},
                "fragment_id": {"type": "integer"},
                "number_of_fragments": {"type": "integer"},
                "id": {"type": "keyword"},
                INDEX_CONTENT_NAME: {
                    "type": "text",
                    "analyzer": "content_analyzer"
                },
                INDEX_CONTENT_EMBEDDING_NAME: {
                    "type": "knn_vector",
                    "dimension": env.EMBEDDING_DIMENSION,
                    "method": {
                        "space_type": "cosinesimil",
                        "name": "hnsw",
                    }
                },
            }
        }
    }

    print(f"[{datetime.datetime.now()}] Configuring index {env.OPENSEARCH_ABSTRACT_FRAGMENT_INDEX}...")
    configure_result = OPENSEARCH_CLIENT.indices.create(index=env.OPENSEARCH_ABSTRACT_FRAGMENT_INDEX, body=settings)
    print(f"[{datetime.datetime.now()}] Configuration result: {configure_result}")


def _bulk_data(documents, index_name):
    for doc in tqdm(documents, file=sys.stdout, total=len(documents)):
        _id: str = doc['id']

        yield {
            "_op_type": "create",
            "_index": index_name,
            "_id": _id,
            "_source": doc,
        }


def fill_index():
    # Load Data
    with open(env.ABSTRACT_FRAGMENT_DATASET_PATH, 'r') as f:
        documents = json.load(f)['documents']

    # Ingest data using the bulk api
    print(f"[{datetime.datetime.now()}] Inserting data into index {env.OPENSEARCH_ABSTRACT_FRAGMENT_INDEX}...")
    generator = _bulk_data(documents, env.OPENSEARCH_ABSTRACT_FRAGMENT_INDEX)
    nb_inserted, errors = helpers.bulk(OPENSEARCH_CLIENT, generator, chunk_size=64, max_retries=2, timeout=60)

    if nb_inserted != len(documents):
        print(f"[{datetime.datetime.now()}] Ingested {nb_inserted}/{len(documents)} fragments.")
        print(f"[{datetime.datetime.now()}] See console output above and below for error details.")
    else:
        print(f"[{datetime.datetime.now()}] Ingested {nb_inserted}/{len(documents)} fragments.")
        print(f"[{datetime.datetime.now()}] {f'Errors: {errors}' if len(errors) > 0 else 'No errors.'}")


if __name__ == "__main__":
    # --------------------------------------------------------------
    # Note: On our M2 MacBook Pro (16GB RAM) ingestion takes > 3h.
    # --------------------------------------------------------------
    # Configure Embedding Model
    configure_opensearch_ml_settings()
    embedding_model_id = initialize_model()
    print(f"[{datetime.datetime.now()}] Running embedding model {embedding_model_id}")

    # Configure Ingest Pipeline and Index
    ingest_pipeline_id = insert_ingest_pipeline(embedding_model_id)
    insert_index(ingest_pipeline_id)

    # Fill Index
    fill_index()
