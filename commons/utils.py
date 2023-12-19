from opensearch_py_ml.ml_commons import MLCommonClient
from opensearchpy import OpenSearch
from typing import Union

def get_model_id(client: Union[MLCommonClient, OpenSearch]):
    if isinstance(client, OpenSearch):
        client = MLCommonClient(client)

    response = client.search_model({
        "query": {
            "match_all": {}
        }
    })

    if response['hits']['total']['value'] == 0:
        raise LookupError("No models found in cluster")
    
    return response['hits']['hits'][0]['_source']['model_id']