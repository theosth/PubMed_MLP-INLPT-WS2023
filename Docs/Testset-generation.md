# Test Set for Document Querying

## General approach

- Take a document, generate questions that can be answered with this document
- Save pair of question and document-id
- For testing our document-retrieval system we can now enter the questions and look whether/with which similarity the correct document gets returned
- For generating the questions we use a strong language model like ChatGPT

## Prompt

First draft:

- Generate a question that can be answered with the context information delimited by triple backticks. The question should be answerable with a simple yes or no. The question should be very specific for this context, meaning that it should only be possible to answer the question when knowing the contents of this context.  Avoid references to meta-information like line numbers.
Limit the output to the generated question.
Context: \```{context}\```


-> Issue: Generated questions contain references like "in this study" 

- Generate a question that can be answered with the context information delimited by triple backticks. The question should be answerable with a simple yes or no. The question should be specific for this context, meaning that it should only be possible to answer the question when knowing the contents of this context. Formulate the question such that it asks for information in a general way, meaning you should avoid references like "this study" or meta-information like line numbers.
Limit the output to the generated question.
Context: ``````

- Generate a question that can be answered with the context information delimited by triple backticks. The question should be answerable with a simple yes or no. The question should be specific for this context, meaning that it should only be possible to answer the question when knowing the contents of this context. The reader of the question has access to this context information as well as to a lot of other articles without knowing to which article this question refers, meaning you should avoid non-specific phrases like "the study" or meta-information like line numbers.
Limit the output to the generated question.
Context: ``````

Generate a question that can be answered with the context information delimited by triple backticks. The question should be answerable with a simple yes or no. Avoid non-specific phrases like "the study" or meta-information like line numbers.
Limit the output to the generated question.
Context: ``````

Generate a question that can be answered with the context information delimited by triple backticks. The question should be answerable with a simple yes or no. Avoid non-specific phrases that require context for the person reading the question.
Limit the output to the generated question.
Context: ``````


Generate a question that can be answered with the context information delimited by triple backticks. The question should be answerable with a simple yes or no. Avoid non-specific phrases that require context for the person reading the question, meaning you should not use references like "the study" which don't make any sense to a reader who doesn't know which study is meant.
Limit the output to the generated question.
Context: ``````

Generate a question that can be answered with the context information delimited by triple backticks. The question should be answerable with a simple yes or no. Only use phrases that don't require context for the person reading the question, meaning you should not use references like "the study" which don't make any sense to a reader who doesn't know which study is meant.
Limit the output to the generated question.
Context: ``````

Generate a question that can be answered with the context information delimited by triple backticks. The question should be answerable with a simple yes or no. Only use phrases that don't require context for the person reading the question, meaning you should not use references like "in the study" because the reader doesn't know which study is meant.
Limit the output to the generated question.
Context: ```

Generate a question that can be answered with the context information delimited by triple backticks. The question should be answerable with a simple yes or no. Only use phrases that don't require context for the person reading the question, meaning you should not use references like "in the study" or "in the context" because the reader of the question doesn't have the context and therefore can not know which study is meant.
Limit the output to the generated question.
Context: ``````


Generate a question that can be answered with the context information delimited by triple backticks. The question should be answerable with a simple yes or no. Only use phrases that don't require context for the person reading the question, meaning you should not use references like "in the study" or "in the context" because the reader of the question doesn't have the context and therefore can not know which study is meant. Take everything written in the context as generally true statements, meaning there is no need to add phrases like "in the text", "in the context", "in the study" or anything equivalent to this.
Limit the output to the generated question.
Context: ``````

Trigger phrases:

- "in the study"
- "in the context"
- "in the sample"
- "in the"
- "in this"


Generate a question that can be answered with the information delimited by triple backticks. The question should be answerable with specific factual information. This means not a yes/no question but a question where some short information is the answer. 
Take everything written in the context as generally true statements, meaning there is no need to add phrases like "in the text", "in the context", "in the study" or anything equivalent to this. The question should never include the words "in the context".
Limit the output to the generated question.
```