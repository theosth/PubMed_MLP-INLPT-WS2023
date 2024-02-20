import json
from opensearchpy import helpers
from opensearchpy.exceptions import NotFoundError
from opensearch_py_ml.ml_commons import MLCommonClient
from opensearch_py_ml.ml_models import SentenceTransformerModel
from development.commons import get_model_id, get_opensearch_client
import sys
from tqdm import tqdm
import development.commons.env as env


content_name = 'abstract_fragment'
content_emb_name = "abstract_fragment_embedding"
embedding_model_download_path = "../scrape/data/embedding_model"

client = get_opensearch_client()


def set_up_embedding_model():
    # Ensure machine learning compatibility
    client.cluster.put_settings({
    "persistent": {
        "plugins": {
        "ml_commons": {
            "only_run_on_ml_node": "false",
            "model_access_control_enabled": "true",
            "native_memory_threshold": "99", 
            "allow_registering_model_via_local_file": "true", # required for using custom ML models
            "allow_registering_model_via_url": "true"  # required for using custom ML models
        }
        }
    }
    })

    # Register embedding model 
    print("Checking if embedding model is already registered...")
    try:
        model_id = get_model_id(client)
        print("Embedding model already registered with id:", model_id)
    except NotFoundError:
        print("Embedding model not registered yet. Registering now...")

        print(f"Setting up model {env.embedding_model_name}. This might take a while...", flush=True)
        print("Downloading model...")
        emb_model = SentenceTransformerModel(model_id=env.embedding_model_name, folder_path=embedding_model_download_path, overwrite=True)
        model_save_path = emb_model.save_as_pt(model_id=env.embedding_model_name, save_json_folder_path=embedding_model_download_path, sentences=["Example sentence"])
        model_config_path = emb_model.make_model_config_json()  # max_length is contained in the tokenizer config

        print("Uploading model...")
        ml_client = MLCommonClient(client)
        model_id = ml_client.register_model(model_save_path, model_config_path, isVerbose=True)
        print("Successfully finished setting up model.")

    print("EMBEDDING MODEL ID:", model_id)

    return model_id


def create_ingest_pipeline(model_id):
    ingest_pipeline_id = "document_ingest_pipeline"
    pipeline_body = {
        "description": "Ingest pipeline for document analysis",
        "processors": [
            {
                "set": {
                    "field": "_source.ingested_at",
                    "value": "{{_ingest.timestamp}}"
                }
            },
            # {
            #     "lowercase": {
            #         "field": "keyword_list"
            #     }
            # },
            {
                "text_embedding": {
                    "model_id": model_id,
                    "field_map": {
                        content_name: content_emb_name
                    }
                }
            }
        ]
    }

    print("Create ingest pipeline", client.ingest.put_pipeline(id=ingest_pipeline_id, body=pipeline_body))
    return ingest_pipeline_id


def create_index(ingest_pipeline_id):
    # delete index if already there. This facilitates "reindexing"
    try: 
        print(f'Delete index {env.opensearch_index_name}:', client.indices.delete(env.opensearch_index_name))
    except NotFoundError:
        pass

    # Index settings
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
                content_name: {
                    "type": "text",
                    "analyzer": "content_analyzer"
                },
                content_emb_name: {
                    "type": "knn_vector",
                    "dimension": env.embedding_dim,
                    "method": {
                        "space_type": "cosinesimil",
                        "name": "hnsw",
                    }
                },
            }
        }
    }

    print(f'Create index {env.opensearch_index_name}:', client.indices.create(index=env.opensearch_index_name, body=settings))


def _bulk_data(documents, index_name):
    for doc in tqdm(documents, file=sys.stdout, total=len(documents)):
        _id: str = doc['id']

        yield {
            "_op_type": "create",
            "_index": index_name,
            "_id": _id,
            "_source": doc,
        }


def ingest_fragments():
    # Load documents
    with open(env.fragment_dataset_location, 'r') as f:
        documents = json.load(f)['documents']

    # Ingest data using the bulk api
    print('Bulk insert data:')
    generator = _bulk_data(documents, env.opensearch_index_name)
    nb_inserted, errors = helpers.bulk(client, generator, chunk_size=64, max_retries=2, timeout=60)
    
    if nb_inserted != len(documents):
        print(f'Only ingested {nb_inserted} of {len(documents)} fragments. See console output above and below for errors.', errors)
    else:
        print(f'Successfully ingested {nb_inserted}/{len(documents)} fragments.', f'Errors: {errors}' if len(errors) > 0 else 'No errors.')


if __name__ == "__main__":
    # ingestion takes 3 hours on my M2 Macbook Pro with 16GB RAM
    model_id = set_up_embedding_model()
    ingest_pipeline_id = create_ingest_pipeline(model_id)
    create_index(ingest_pipeline_id)
    ingest_fragments()