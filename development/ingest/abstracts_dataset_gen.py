import datetime
import json
import os
import sys

from tqdm import tqdm

import development.commons.env as env


def load_dataset():
    print(f"[{datetime.datetime.now()}] Loading Documents")
    with open(env.CLEANED_DATASET_PATH, 'r') as input:
        dataset = json.load(input)
    return dataset


def restructure(dataset):
    print(f"[{datetime.datetime.now()}] Restructuring dataset...")
    documents = dataset["documents"]
    abstracts = []

    for document in tqdm(documents, total=len(documents), file=sys.stdout):
        abstracts.append(document)

    print(f"[{datetime.datetime.now()}] Collected {len(abstracts)} abstracts from {len(documents)} documents")
    dataset = {
        'dataset_scraped_on': dataset['dataset_scraped_on'],
        'dataset_cleaned_on': dataset['dataset_cleaned_on'],
        'dataset_fragmented_on': datetime.datetime.now(),
        'documents': abstracts
    }
    return dataset


def save_abstracts(abstracts):
    # Ensure target folder exists
    folder_path = os.path.dirname(env.ABSTRACTS_DATASET_PATH)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    print(f"[{datetime.datetime.now()}] Saving Abstracts ({env.ABSTRACTS_DATASET_PATH})")
    with open(env.ABSTRACTS_DATASET_PATH, 'w') as output:
        json.dump(abstracts, output, indent=2, default=str)
    print(f"[{datetime.datetime.now()}] Abstracts successfully saved!")


def main():
    dataset = load_dataset()
    abstracts = restructure(dataset)
    save_abstracts(abstracts)


if __name__ == '__main__':
    main()
