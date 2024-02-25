import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import development.commons.env as env
from opensearchpy import OpenSearch


def get_opensearch_client():
    return OpenSearch(
        hosts=[{'host': env.OPENSEARCH_HOST, 'port': env.OPENSEARCH_PORT}],
        http_auth=env.OPENSEARCH_AUTH,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )
