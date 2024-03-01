import datetime
import json
import pickle
import sys

from tqdm import tqdm

import development.commons.env as env

# ===== Constants =====
ABSTRACT_JOIN_SEPARATOR = "\n"
AUTHOR_NAME_SEPARATOR = " "
# ===== Constants =====


def load_documents():
    print(f"[{datetime.datetime.now()}] Loading 1.4GB of Documents ({env.RAW_DATASET_PATH})...")
    with open(env.RAW_DATASET_PATH, "rb") as input:
        documents = pickle.load(input)
    print(f"[{datetime.datetime.now()}] Documents successfully loaded!")
    return documents


def is_missing_abstract(medium):
    return ("Abstract" not in medium or
            "AbstractText" not in medium["Abstract"] or
            len(medium["Abstract"]["AbstractText"]) == 0)


def is_missing_author(medium):
    return "AuthorList" not in medium or len(medium["AuthorList"]) == 0


def extract_doi(elocids):
    elocids = list(filter(lambda v: v.attributes["EIdType"] == "doi", elocids))
    if len(elocids) == 0:
        return ''
    assert len(elocids) == 1
    return str(elocids[0])


def extract_authors(authors):
    return [AUTHOR_NAME_SEPARATOR.join(filter(lambda s: s != "", [
        author.get('ForeName', ''),
        author.get('LastName', ''),
        author.get('CollectiveName', '')]))
        for author in authors
    ]


def extract_publication_date(document):
    history = document["PubmedData"]["History"]
    newest_entry = history[-1]

    # Ensure that every document has a publication date
    if len(history) == 0:
        print(json.dumps(document, indent=4))

    publication_date = datetime.datetime(
        int(newest_entry["Year"]),
        int(newest_entry["Month"]),
        int(newest_entry["Day"])
    ).date()

    return publication_date


def extract_articles(batch):
    documents = []
    articles_without_abstract = 0
    articles_without_authors = 0

    for article in batch["PubmedArticle"]:
        # Unpack Article Hierarchy
        outer_article = article["MedlineCitation"]
        inner_article = outer_article["Article"]

        # Validate Article
        if is_missing_abstract(inner_article):
            articles_without_abstract += 1
            continue

        if is_missing_author(inner_article):
            articles_without_authors += 1

        # Extract Document Properties
        pmid = outer_article["PMID"]
        doi = extract_doi(inner_article.get("ELocationID", []))
        title = inner_article["ArticleTitle"]
        author_list = extract_authors(inner_article.get("AuthorList", []))
        abstract = ABSTRACT_JOIN_SEPARATOR.join(inner_article["Abstract"]["AbstractText"])
        publication_date = extract_publication_date(article)
        keyword_list = [e for elem in outer_article["KeywordList"] for e in elem]

        cleaned_article = {
            "pmid": pmid,
            "doi": doi,
            "title": title,
            "author_list": author_list,
            "abstract": abstract,
            "publication_date": publication_date,
            "keyword_list": keyword_list,
        }
        documents.append(cleaned_article)

    return documents, articles_without_abstract, articles_without_authors


def extract_books(batch):
    documents = []
    books_without_abstract = 0
    books_without_authors = 0

    for book in batch["PubmedBookArticle"]:
        # Unpack Book
        outer_book = book["BookDocument"]
        inner_book = outer_book["Book"]

        # Validate Book
        if is_missing_abstract(book):
            books_without_abstract += 1
            continue

        if is_missing_author(book):
            books_without_authors += 1

        # Extract Document Properties
        pmid = book["PMID"]
        doi = extract_doi(inner_book.get('ELocationID', []))
        title = inner_book["BookTitle"]
        author_list = extract_authors([a for list in inner_book.get("AuthorList", []) for a in list])
        abstract = ABSTRACT_JOIN_SEPARATOR.join(book["Abstract"]["AbstractText"])
        publication_date = extract_publication_date(inner_book)
        keyword_list = [e for elem in book["KeywordList"] for e in elem]

        cleaned_article = {
            "pmid": pmid,
            "doi": doi,
            "title": title,
            "author_list": author_list,
            "abstract": abstract,
            "publication_date": publication_date,
            "keyword_list": keyword_list,
        }
        documents.append(cleaned_article)

    return documents, books_without_abstract, books_without_authors


def extract_relevant_information(data):
    print(f"[{datetime.datetime.now()}] Extracting relevant information....")
    documents_without_abstract = 0
    documents_without_author = 0
    documents = []

    for batch in tqdm(data["batched_data"], file=sys.stdout):
        # Extract "Articles"
        articles, articles_without_abstract, articles_without_author = extract_articles(batch)
        documents.extend(articles)
        documents_without_abstract += articles_without_abstract
        documents_without_author += articles_without_author

        # Extract "Books"
        books, books_without_abstract, books_without_author = extract_books(batch)
        documents.extend(books)
        documents_without_abstract += books_without_abstract
        documents_without_author += books_without_author

    print()
    print(f"[{datetime.datetime.now()}] Extraction Statistics:")
    print(f"Scraping Timestamp: {data['timestamp']}")
    print(f"Total Documents: {len(documents) + documents_without_abstract}")
    print(f"Valid Documents: {len(documents)}")
    print(f"Invalid Documents: {documents_without_abstract}")
    print(f"Author-less Documents: {documents_without_author}")
    print()

    extraction = {
        "dataset_scraped_on": data["timestamp"],
        "dataset_cleaned_on": datetime.datetime.now(),
        "documents": documents
    }
    return extraction


def save_extraction(extraction):
    print(f"[{datetime.datetime.now()}] Saving extracted relevant information...")
    with open(env.CLEANED_DATASET_PATH, "w") as output:
        json.dump(extraction, output, indent=2, default=str)
    print(f"[{datetime.datetime.now()}] Information successfully saved to {env.CLEANED_DATASET_PATH}!")


def main():
    documents = load_documents()
    extraction = extract_relevant_information(documents)
    save_extraction(extraction)


if __name__ == '__main__':
    main()
