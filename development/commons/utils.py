import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import development.commons.env as env

from typing import Union

from opensearch_py_ml.ml_commons import MLCommonClient
from opensearchpy import OpenSearch
from opensearchpy.exceptions import NotFoundError


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
