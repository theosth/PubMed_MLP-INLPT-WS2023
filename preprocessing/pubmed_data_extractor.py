import json
import pickle
import datetime
import sys

from tqdm import tqdm

abstract_join_string = '\n'  # used to join abstracts that are defined in parts

print(f'[{datetime.datetime.now()}] Loading raw data (this might take a few minutes and requires roughly 14 GB memory)...')
with open('data/raw.pkl', 'rb') as f:
    raw = pickle.load(f)
print(f'[{datetime.datetime.now()}] Raw data loaded.')


def extract_doi(elocids):
    elocids = list(filter(lambda v: v.attributes['EIdType'] == 'doi', elocids))
    if len(elocids) == 0:
        return ''
    assert len(elocids) == 1
    return str(elocids[0])


def extract_authors(authors):
    name_separator = " "
    return [name_separator.join(filter(lambda s: s != "", [a.get('ForeName', ''), a.get('LastName', ''), a.get('CollectiveName', '')])) for a in authors]


print(f"cleaning raw data...")
nb_without_abstract = 0
nb_articles_without_author = 0
documents = []
for batch in tqdm(raw['batched_data'], file=sys.stdout):
    for article in batch['PubmedArticle']:
        article = article['MedlineCitation']
        inner_article = article['Article']
        if 'Abstract' not in inner_article or 'AbstractText' not in inner_article['Abstract'] or len(inner_article['Abstract']['AbstractText']) == 0:
            nb_without_abstract += 1
            continue

        if 'AuthorList' not in inner_article or len(inner_article['AuthorList']) == 0:
            nb_articles_without_author += 1

        publication_date = [datetime.datetime(int(d['Year']), int(d['Month']), int(d['Day'])) for d in inner_article['ArticleDate']]
        assert len(publication_date) < 2
        cleaned_article = {
            'pmid': article['PMID'],  # pubmed id
            'doi': extract_doi(inner_article.get('ELocationID', [])),
            'title': inner_article['ArticleTitle'],
            'author_list': extract_authors(inner_article.get('AuthorList', [])),
            'abstract': abstract_join_string.join(inner_article['Abstract']['AbstractText']),  # join paragraphed abstracts
            'publication_date': publication_date[0] if len(publication_date) >= 1 else None,
            'keyword_list': [e for elem in article['KeywordList'] for e in elem],
        }
        documents.append(cleaned_article)

    for book in batch['PubmedBookArticle']:
        book = book['BookDocument']
        inner_book = book['Book']

        if 'Abstract' not in book or 'AbstractText' not in book['Abstract'] or len(book['Abstract']['AbstractText']) == 0:
            nb_without_abstract += 1
            continue

        if 'AuthorList' not in inner_book or len(inner_book['AuthorList']) == 0:
            nb_articles_without_author += 1

        publication_date = datetime.datetime(int(inner_book['PubDate']['Year']), int(inner_book['PubDate'].get('Month', '01')), int(inner_book['PubDate'].get('Day', '01')))
        cleaned_article = {
            'pmid': book['PMID'],  # pubmed id
            'doi': extract_doi(inner_book.get('ELocationID', [])),
            'title': inner_book['BookTitle'],
            'author_list': extract_authors([a for list in inner_book.get('AuthorList', []) for a in list]),
            'abstract': abstract_join_string.join(book['Abstract']['AbstractText']),  # join paragraphed abstracts
            'publication_date': publication_date,
            'keyword_list': [e for elem in book['KeywordList'] for e in elem],
        }
        documents.append(cleaned_article)

print()
print(f'[{datetime.datetime.now()}] STATS:')
print("Number of documents in original raw data:", len(documents) + nb_without_abstract)
print("Number of documents without any authors in raw data:", nb_articles_without_author)
print("Raw data scraped on:", raw['timestamp'])
print("---")
print(f"Number of documents in cleaned dataset:", len(documents))
print("Number of documents discarded from raw data due to missing an abstract:", nb_without_abstract)
print()

dataset = {'dataset_scraped_on': raw['timestamp'],
           'dataset_cleaned_on': datetime.datetime.now(),
           'documents': documents}

print('saving cleaned dataset as json...')
with open('data/dataset.json', 'w') as f:
    json.dump(dataset, f, indent=2, default=str)
print('cleaned dataset saved as json.')

print('saving cleaned dataset as pickle...')
with open('data/dataset.pkl', 'wb') as f:
    pickle.dump(dataset, f)
print('cleaned dataset saved as pkl.')
