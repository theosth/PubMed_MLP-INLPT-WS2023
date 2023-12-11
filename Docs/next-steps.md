For our next steps we have to think about the following questions. We grouped the main points by the parts of the system that we want to build.


- Save documents in (vector) database
    - What is a document: How many tokens/sentences get summarized as one document?
        - Just take paragraphs
            - If paragraph is too large, split into multiple documents (if possible dont cut in the middle of a sentence)
        - Take fixed token size
        - Take fixed token size with overlap
    - How large should one chunk ideally be? Should we aim at ~500 tokens (to max out input size of bert)
- Document retrieval
    - What information do we use for retrieval? How can use metadata, emphasize title, etc.
    - How do we evaluate similarity between document and query
        - Only syntactical (baseline, BM-25)
        - Only semantical
        - Hybrid
- Getting from retrieved documents to context that can be handled by model
    - Creative idea: Condense multiple documents by summarizing with regards to specific question → Reduce token size → Fit more info when querying model
        - this can e.g. be used to fit more context from the abstract of the highest scoring document into the prompt for generating the answer
    - Only use highest scoring document
- Actual question answering
    - What model do we use?
    - Should/Can we fine-tune the model? (answer types)