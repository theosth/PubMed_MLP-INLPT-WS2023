# OpenSearch
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200
OPENSEARCH_AUTH = ('admin', 'admin')

# Data Indices
OPENSEARCH_FRAGMENT_INDEX = "fragments"
OPENSEARCH_ABSTRACT_INDEX = "abstracts"

# Embedding
EMBEDDING_MODEL_NAME = "pritamdeka/S-PubMedBert-MS-MARCO"
EMBEDDING_DIMENSION = 768
FRAGMENT_OVERLAP = 32
TOKENS_PER_FRAGMENT = 256

# Data Flow
FRAGMENT_DATASET_PATH = "data/fragments2.json"
RAW_DATASET_PATH = "development/scrape/data/raw.pkl"
CLEANED_DATASET_PATH = "../scrape/data/dataset.json"
