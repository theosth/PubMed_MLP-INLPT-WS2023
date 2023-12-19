import json
from tqdm import tqdm
import sys
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
import datetime
import commons.env as env

embed_model_id = env.embedding_model_name
chunk_overlap = 32
token_per_chunk = 256

print("Loading text splitter using tokenizer of model:", embed_model_id)
splitter = SentenceTransformersTokenTextSplitter(
    model_name=embed_model_id,  
    chunk_overlap=chunk_overlap,  
    tokens_per_chunk=token_per_chunk
)

print("Loading dataset...")
with open('data/dataset.json', 'r') as f:
    dataset = json.load(f)

documents = dataset['documents']

print("Splitting documents into fragments...")
fragments = []
for doc in tqdm(documents, total=len(documents), file=sys.stdout):
    chunks = splitter.split_text(text=doc['abstract'])
    
    for i, c in enumerate(chunks):
        doc_chunk = doc.copy()

        del doc_chunk['abstract']
        doc_chunk['fragment_id'] = i
        doc_chunk['number_of_fragments'] = len(chunks) 
        doc_chunk['abstract_fragment'] = c
        doc_chunk['id'] = f"{doc['pmid']}_{i}"

        fragments.append(doc_chunk)

print(f"Collected {len(fragments)} fragments from {len(documents)} documents")

dataset = {'dataset_scraped_on': dataset['dataset_scraped_on'],
           'dataset_cleaned_on': dataset['dataset_cleaned_on'],
           'dataset_fragmented_on': datetime.datetime.now(),
           'documents': fragments}

loc = env.fragment_dataset_location
print("Saving fragmented dataset to", loc)
with open(loc, 'w') as f:
    json.dump(dataset, f, indent=2, default=str)
print("Success!")