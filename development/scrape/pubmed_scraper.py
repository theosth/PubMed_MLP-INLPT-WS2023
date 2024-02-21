import datetime
import math
import pickle

from Bio import Entrez
from tqdm import tqdm

import development.commons.env as env

# ===== Constants =====
DATABASE_NAME = "pubmed"
ANSWER_FORMAT = "xml"
SEARCH_TERM = "intelligence[Title/Abstract]"
ID_BATCH_SIZE_LIMIT = 10000
DOC_BATCH_SIZE_LIMIT = 1000
# ===== Constants =====


def fetch_relevant_document_ids(start_year, end_year, checkpoints_per_year):
    Entrez.email = 'benedikt.vidic@gmx.de'
    relevant_ids = []

    for checkpoint in range(0, (end_year - start_year) * checkpoints_per_year):
        # Define time span
        year = start_year + math.floor(checkpoint / checkpoints_per_year)
        start_month = '01' if checkpoint % 2 == 0 else '07'
        end_month = '06' if checkpoint % 2 == 0 else '12'

        # Retrieve document handles for that time span
        batch_result = Entrez.read(
            Entrez.esearch(db=DATABASE_NAME,
                           retstart=0,
                           retmax=ID_BATCH_SIZE_LIMIT,  # 10000 ids per fetch is an api limit
                           retmode=ANSWER_FORMAT,
                           mindate=str(year) + '/' + start_month,
                           maxdate=str(year) + '/' + end_month,
                           term=SEARCH_TERM
                           )
        )

        # Extract document ids
        batch_ids = batch_result["IdList"]
        print(f"Batch ID Count: {len(batch_ids)}")
        relevant_ids += batch_ids

    print(f"Total ID Count: {len(relevant_ids)}")
    return relevant_ids


def fetch_relevant_documents(relevant_document_ids):
    relevant_documents = []
    for index in tqdm(range(0, len(relevant_document_ids), DOC_BATCH_SIZE_LIMIT)):
        batch_documents = Entrez.read(
            Entrez.efetch(
                db=DATABASE_NAME,
                id=relevant_document_ids[index:index + DOC_BATCH_SIZE_LIMIT],
                retmode=ANSWER_FORMAT
            )
        )
        relevant_documents.append(batch_documents)
    return relevant_documents


def save_relevant_documents(relevant_documents):
    print("Saving Documents...")
    with open(env.RAW_DATASET_PATH, "wb") as output:
        pickle.dump({
            'batched_data': relevant_documents,
            'timestamp': datetime.datetime.now()
        }, output)

    print("Documents successfully saved!")


def main():
    relevant_document_ids = fetch_relevant_document_ids(
        start_year=2013,
        end_year=2024,
        checkpoints_per_year=2
    )

    # Assert ID uniqueness
    assert len(relevant_document_ids) == len(set(relevant_document_ids))

    relevant_documents = fetch_relevant_documents(relevant_document_ids)
    save_relevant_documents(relevant_documents)


if __name__ == '__main__':
    main()
