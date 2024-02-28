# OpenSearch
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200
OPENSEARCH_AUTH = ('admin', 'admin')

# Data Indices
OPENSEARCH_ABSTRACT_FRAGMENT_INDEX = "abstract_fragments"
OPENSEARCH_ABSTRACT_INDEX = "abstracts"

# Embedding
EMBEDDING_MODEL_NAME = "pritamdeka/S-PubMedBert-MS-MARCO"
EMBEDDING_MODEL_PATH = "../ingest/data/embedding_model"
EMBEDDING_DIMENSION = 768
FRAGMENT_OVERLAP = 32
TOKENS_PER_FRAGMENT = 256

# Language Model
OLLAMA_MODEL_NAME = "mistral"
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11443

# Data Flow
ABSTRACTS_DATASET_PATH = "data/dataset.json"
ABSTRACT_FRAGMENT_DATASET_PATH = "data/fragment-dataset.json"
RAW_DATASET_PATH = "development/scrape/data/raw.pkl"
CLEANED_DATASET_PATH = "../scrape/data/dataset.json"
