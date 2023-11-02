from Bio import Entrez
import math
from tqdm import tqdm
import pickle
import datetime
import os

Entrez.email = 'benedikt.vidic@gmx.de'

allIds = []

for x in range(0,22):
    year = 2013 + math.floor(x/2)
    startMonth = '01' if x%2 == 0 else '07'
    endMonth = '06' if x%2 == 0 else '12'

    handle = Entrez.esearch(db='pubmed',
    retstart=0,
    retmax='10000', #10000 ids per fetch is an api limit
    retmode='xml',
    mindate=str(year)+'/'+startMonth,
    maxdate=str(year)+'/'+endMonth,
    term='intelligence[Title/Abstract]')

    result = Entrez.read(handle)

    batch_ids = result['IdList']
    print('ids in batch:',len(batch_ids))
    allIds += batch_ids

print('total number of IDs fetched:')
print(len(allIds))
assert len(allIds) == len(set(allIds))  # assert unique IDs

batch_size = 1000
all_results = []
for i in tqdm(range(0, len(allIds), batch_size)):
    handle = Entrez.efetch(db='pubmed', id=allIds[i:i + batch_size])
    # handle = Entrez.efetch(db='pubmed', id=allIds[i:i+step_size], rettype='docsum', retmode='xml')
    batch = Entrez.read(handle)
    all_results.append(batch)
print('download to memory complete.')

#abstracts = [article['MedlineCitation']['Article']['Abstract']['AbstractText'] for article in result['PubmedArticle']]

print('saving results...')
if not os.path.exists('data'):
    os.mkdir('data')
with open('data/raw.pkl', 'wb') as f:
    pickle.dump({'batched_data': all_results, 'timestamp': datetime.datetime.now()}, f)
print('results saved as pkl.')
