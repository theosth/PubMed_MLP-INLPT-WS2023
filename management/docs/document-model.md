# Document Model

Each abstract is split into fragments using the `SentenceTransformersTokenTextSplitter` of the `langchain` library. 
It is used to accurately split texts for the specific embedding model used (which is Huggingface's `pritamdeka/S-PubMedBert-MS-MARCO` (350 token model) in our case). 

Additionally, we define an overlap of 32 tokens of each fragment, to capture semantic context more coherently and to avoid breaking context too abruptly, 
in case an answer is at the splitting point of two fragments. This ensures the answer can still be answered using either fragment instead of being lost. 
Example:
- Full text: The Declaration of Independence was signed by George Washington earlier that year.
- Split without overlap: ["The Declaration of Independence was signed by George", "Washington earlier that year."]
- Split with overlap: ["The Declaration of Independence was signed by George Washington earlier", "signed by George Washington earlier that year."]
- Question: By whom was the Declaration of Independence signed?
In this example, the split without overlap could not answer the question fully because of missing context / the answer being split across fragments. With overlap we aim to minimize the probability of this happening. The number 32 was more or less arbitrarily chosen. However, the research points out that the overlap is highly application dependent 
and should include enough overlap to augment the fragment in a meaningful way instead of just a few words. Furthermore it should not be too large, as this leads to indistinct fragments,
thus blurring the line between fragments during semantic text search. 

Moreover, we noticed that in a first run, where we left the `tokens_per_chunk` parameter untouched, we received 76146 fragments from 55924 documents. 
This means that, on average, each abstract yielded 1.36x fragments. By inspecting the resulting fragments, we found that oftentimes most of the abstract 
test was contained in the first fragment, where the second fragment only included the tail of the document.
In these cases, the second fragment doesn't include a lot of meaning, so that the chunking process effectively equates a truncation process. 
To remedy this, we set a `tokens_per_chunk` number lower than the limit of 350 tokens.  
As an addition, this facilitates the later question answering process because here the QA model has to receive the context **and** a question. 
If the context is already 350 tokens long, there is no space for the question.  
To comfortably accommodate the question, as well as to make the second fragment more meaningful, we settle for a `tokens_per_chunk` of **256** tokens.  
With this token limit, the number of fragments rose to 101571 fragments and the factor to 1,82. 

Furthermore, we thought about splitting the abstract at paragraphs first, before then running it through the token splitter. However, this yields fragments where for example the 
result paragraph of the abstract is in its own fragment, but reading these paragraphs on their own is really confusing and doesn't give much insight, since you just read some random results, without knowing what they are results of. However, often the answer to a specific question can be found in the result paragraph. But without knowing the context of the results, they are worthless. By not splitting at paragraph boundries, the result paragraph is combined with the previous paragraph, thus giving the results some context. 

Lastly, we decided against including any of the metadata in the fragment text to be embedded for semantic search. Instead, we tackle this by evaluating a hybrid search. 
We hope to enrich our search with this hybrid search in a meaningful, more interpretable, easier and more structured way, as opposed to including the information in the text data.

## Document Splitting Bug

While developing and experimenting with our retriever we sometimes encountered unusually short document fragments, even shorter than our overlap window for the document splitting. This kind of fragment should not exist. This is an issue because these fragments do not provide useful information for generating answers but potentially achieve exceptionally high scores by our retrieving system because they are so short.
After looking further into it we discovered that this weren't just a few exceptions. We found 8109 fragments that only included text that is already fully present in their preceding fragment (The code to find and count these documents can be found in development/ingest/analyse_fragment_split.py).
We could track it down to a bug in the langchain Text Splitter that was not accounting for the overlap when checking whether to add a new fragment. At the point we discovered this, the bug was already fixed in december in a new langchain version ([Github commit that fixed this](https://github.com/langchain-ai/langchain/commit/ea331f31364266f7a6414dc76265553a52279b0a)). Therefore the solution for us to clean up the fragments simply consisted of updating the langchain version and redoing the document splitting and opensearch ingestion.
