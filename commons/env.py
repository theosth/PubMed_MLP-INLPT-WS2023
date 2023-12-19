# Opensearch creds
opensearch_host = 'localhost'  # Replace with your opensearch host
opensearch_port = 9200  # Replace with your opensearch port
opensearch_auth = ('admin', 'admin')  # Replace with your opensearch creds

opensearch_index_name = 'abstracts'

embedding_model_name = 'pritamdeka/S-PubMedBert-MS-MARCO'
embedding_dim = 768  # must match output of embedding model

fragment_dataset_location = 'data/fragment-dataset.json' # should be relative to root of project
