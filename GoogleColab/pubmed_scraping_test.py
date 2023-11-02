from Bio import Entrez
import math

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
    print('batch size:',len(batch_ids))
    allIds += batch_ids

print('total size:')
print(len(allIds))
assert len(allIds) == len(set(allIds))  # assert unique IDs

handle = Entrez.efetch(db='pubmed', id=allIds[:1000])
# handle = Entrez.efetch(db='pubmed', id=allIds[:10], rettype='docsum', retmode='xml')
result = Entrez.read(handle)

#abstracts = [article['MedlineCitation']['Article']['Abstract']['AbstractText'] for article in result['PubmedArticle']]

import pickle
with open('test.pkl', 'wb') as f:
  pickle.dump(result, f)

# with open('test_abstract.pkl', 'wb') as f:
#   pickle.dump(abstracts, f)