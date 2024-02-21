from opensearch_py_ml.ml_commons import MLCommonClient
from opensearchpy.exceptions import NotFoundError
from opensearchpy import OpenSearch
from typing import Union
import development.commons.env as env

def get_model_id(client: Union[MLCommonClient, OpenSearch]):
    if isinstance(client, OpenSearch):
        client = MLCommonClient(client)

    response = client.search_model({
        "query": {
            "match_all": {}
        }
    })

    if response['hits']['total']['value'] == 0:
        raise NotFoundError("No models found in cluster")

    return response['hits']['hits'][0]['_source']['model_id']

def get_opensearch_client():
    return OpenSearch(
        hosts=[{'host': env.OPENSEARCH_HOST, 'port': env.OPENSEARCH_PORT}],
        http_auth=env.OPENSEARCH_AUTH,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )