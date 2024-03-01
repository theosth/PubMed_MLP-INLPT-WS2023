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
ABSTRACTS_DATASET_PATH = "../ingest/data/abstracts_dataset.json"
ABSTRACT_FRAGMENT_DATASET_PATH = "../ingest/data/abstract_fragment_dataset.json"
RAW_DATASET_PATH = "../scrape/data/raw_retrieved_dataset.pkl"
CLEANED_DATASET_PATH = "../scrape/data/cleaned_retrieved_dataset.json"

# Testing
RAGAS_TESTSET_PATH = "development/evaluate/retrieval/testsets/ragas-testset.json"
RAGAS_UDATED_TESTSET_PATH = "development/evaluate/retrieval/testsets/ragas-updated-testset.json"
RETRIEVAL_RAGAS_EVAL_RESULT_PATH = "development/evaluate/retrieval/results/retriever_ragas_eval_result.json"

RETRIEVAL_TESTSET_PATH = "development/evaluate/retrieval/testsets/retrieval-testset.json"
RETRIEVAL_RESULT_FOLDER_PATH = "development/evaluate/retrieval/results/"