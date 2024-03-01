import datetime
import json
import os
import sys

from langchain.text_splitter import SentenceTransformersTokenTextSplitter
from tqdm import tqdm

import development.commons.env as env


def load_document_splitter():
    print(f"[{datetime.datetime.now()}] Loading Document Splitter ({env.EMBEDDING_MODEL_NAME})")
    return SentenceTransformersTokenTextSplitter(
        model_name=env.EMBEDDING_MODEL_NAME,
        chunk_overlap=env.FRAGMENT_OVERLAP,
        tokens_per_chunk=env.TOKENS_PER_FRAGMENT
    )


def load_dataset():
    print(f"[{datetime.datetime.now()}] Loading Documents")
    with open(env.CLEANED_DATASET_PATH, 'r') as input:
        dataset = json.load(input)
    return dataset


def split_documents(dataset, splitter):
    print(f"[{datetime.datetime.now()}] Splitting Documents...")
    documents = dataset["documents"]
    fragments = []

    for document in tqdm(documents, total=len(documents), file=sys.stdout):
        abstract_fragments = splitter.split_text(text=document['abstract'])
        for index, fragment in enumerate(abstract_fragments):
            document_fragment = document.copy()

            del document_fragment['abstract']
            document_fragment['fragment_id'] = index
            document_fragment['number_of_fragments'] = len(abstract_fragments)
            document_fragment['abstract_fragment'] = fragment
            document_fragment['id'] = f"{document['pmid']}_{index}"
            fragments.append(document_fragment)

    print(f"[{datetime.datetime.now()}] Collected {len(fragments)} fragments from {len(documents)} documents")
    dataset = {
        'dataset_scraped_on': dataset['dataset_scraped_on'],
        'dataset_cleaned_on': dataset['dataset_cleaned_on'],
        'dataset_fragmented_on': datetime.datetime.now(),
        'documents': fragments
    }
    return dataset


def save_fragments(fragments):
    folder_path = os.path.dirname(env.ABSTRACT_FRAGMENT_DATASET_PATH)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    print(f"[{datetime.datetime.now()}] Saving Fragments ({env.ABSTRACT_FRAGMENT_DATASET_PATH})")
    with open(env.ABSTRACT_FRAGMENT_DATASET_PATH, 'w') as output:
        json.dump(fragments, output, indent=2, default=str)
    print(f"[{datetime.datetime.now()}] Fragments successfully saved!")


def main():
    splitter = load_document_splitter()
    dataset = load_dataset()
    fragments = split_documents(dataset, splitter)
    save_fragments(fragments)


if __name__ == '__main__':
    main()
