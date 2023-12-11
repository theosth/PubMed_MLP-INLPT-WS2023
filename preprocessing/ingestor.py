import json
from opensearchpy import OpenSearch, helpers
from opensearchpy.exceptions import NotFoundError
import sys
from tqdm import tqdm

# Opensearch creds
host = 'localhost'  # Replace with your opensearch host
port = 9200  # Replace with your opensearch port
auth = ('admin', 'admin')  # Replace with your opensearch creds

index_name = 'abstracts'

client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

content_name = 'abstract'
pipeline_id = "document_ingest_pipeline"

pipeline_body = {
    "description": "Ingest pipeline for document analysis",
    "processors": [
        # {
        #     "set": {
        #         "field": "_source.imported_at",
        #         "value": "{{_ingest.timestamp}}"
        #     }
        # },
        # {
        #     "lowercase": {
        #         "field": "keyword_list"
        #     }
        # },
    ]
}

print("Create ingest pipeline", client.ingest.put_pipeline(id=pipeline_id, body=pipeline_body))

# delete index if already there. This facilitates "reindexing"
try: 
    print(f'Delete index {index_name}:', client.indices.delete(index_name))
except NotFoundError:
    pass

# Index settings
settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "index.knn": True,
        "default_pipeline": pipeline_id,
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
            content_name: {
                "type": "text",
                "analyzer": "content_analyzer"
            },
        }
    }
}

# Create the index with the specified settings and mappings
print(f'Create index {index_name}:', client.indices.create(index=index_name, body=settings))


# Ingest documents
with open('data/dataset.json', 'r') as f:
    documents = json.load(f)['documents']

def bulk_data(documents, index_name):
    for doc in tqdm(documents, file=sys.stdout):
        _id: str = doc['pmid']

        yield {
            "_op_type": "create",
            "_index": index_name,
            "_id": _id,
            "_source": doc,
        }

# Ingest data using the bulk api
print('Bulk insert data:')
nb_inserted, errors = helpers.bulk(client, bulk_data(documents, index_name))
    
print(f'Successfully inserted {nb_inserted} documents.', f'Errors: {errors}' if len(errors) > 0 else 'No errors.')

