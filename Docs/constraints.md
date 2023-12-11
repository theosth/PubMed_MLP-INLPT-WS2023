## Constraints of our system:

- Which question types should our system be able to answer?
    - Yes/No/(Maybe)
    - Factual questions
        - Either as a complete sentence or as a concise statement → Depends on the model/architecture we’re going to use
- Which types of answers should our system produce?
    - First extractive answering and then also try to achieve abstractive answering
    - Including a source → Which abstract is the answer based on? Which exact document(s)/span of the abstract is the answer based on?
    - What about producing multiple answers? E.g. one answer based on each abstract that came up as relevant
    - Nice to have: Include metrics about how “sure” the answer is. E.g. how high was the similarity between question and document the answer is based on

- Probably we’ll set a fixed max-question-length