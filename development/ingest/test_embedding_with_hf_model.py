import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import development.commons.env as env
import development.commons.utils as utils

from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# load documents from json
with open(env.ABSTRACT_FRAGMENT_DATASET_PATH) as f:
    data = json.load(f)
documents = data['documents']

# only use the first 10 documents for now
documents = documents[:10000]

# abstract_fragments
abstract_fragments = [documents[i]['abstract_fragment'] for i in range(len(documents))]

# embed
model = SentenceTransformer(env.EMBEDDING_MODEL_NAME)


# instead embed in batches
embeddings = []
batch_size = 100
for i in tqdm(range(0, len(abstract_fragments), batch_size)):
    embeddings.extend(model.encode(abstract_fragments[i:i+batch_size]))
    
# save embeddings