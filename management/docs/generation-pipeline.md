# Generation Pipeline

## Choice of Generation Backend

### Model
We chose Llama2 because 

### Framework
Unfortunately, with our setup, we can not use Google Colab. This is because Google Colab can only access publicly hosted databases, which our OpenSearch instance is not because we have no server for it. This is why we need to ensure hardware acceleration with local devices.

We chose Ollama as backend for Llama2 because hardware acceleration is essential in order to receive answers in real time. 
However, getting the hardware acceleration set-up properly is very time-consuming and cumbersome with other solutions. 
To improve the user experience and workflow for our team we evaluated the following frameworks:
- Downloading the model directly and quantizing it ourselves: The quantization process takes quite a lot of time and space.   
Also, on Windows, the libraries are not updated to perform 4bit quantization without custom C++ compilation. It is much better to use an already quantized model.
- CTransformers: It allows for downloading already quantized models. However, it is extremely hard to get hardware acceleration working on MacOS.
- LlamaCpp: It also allows for downloading already quantized models, but it requires a lot of manual configuration for hardware acceleration.
- Ollama: It provides by far the easiest setup (as easy as installing any app), allows for already quantized models and, additionally, it has Langchain support.


## Choice of Generation Model 

We did several tests with different light-weight generation models to determine which model is fit best for our application. We decided to use a light-weight model in order to execute it on most common personal devices. These models are usually in the range of 3-5 GB disk storage and fit into most devices with 8-16 GB memory. They offer good performance for their small size and should be sufficient to do simple question answering.

### Llama 2

For our test with Meta's Llama 2 model, we used a 4 bit quantized version of the 7 billion parameter model. It requires 3.8 GB of disk space. The next largest model with 13 billion parameters and 7.2 GB in disk space already exceeds the limits for our use case and the ability to use it with local machines. 

Llama 2 showed bad performance especially when it came to adhering to the prompt and its instructions. It frequently ignored prompt instructions and added seemingly random information to the answer. Questions with missing context were often met with hallucinations. Even with very simple prompts and test data it was hard to get a satisfactory result. The additions of weird part of text were not controllable with temperature adjustments. Here are some negative examples: 

Prompt Template:
    - Give just the answer to the following user query ```{query}``` using the information given in
context ```{context}```.
In the case there is no relevant information in the provided context,
try to answer yourself, but tell the user that you did not have any
relevant context to base your answer on. Be concise and factual. 

Context: 
    - "Jesse loves red but not yellow"
    - "Jamal loves green but not as much as he loves orange"
    - "Jesse's favorite color is red"

Question:
    - "Is Jesse's favorite color orange?"
    - "What is Theo's favorite color?"
    - "Are penguins birds?"

Answer:
    - Jesse's favorite color is not specified in the provided context, so I cannot accurately determine their favorite color. (While this is technically true, it could say that Jesse likes red.)
    - Theo's favorite color is... (checking the provided context) ...orange. (Hallucination and weird answer.)
    - Yes, penguins are birds. (Correct, but did not mention that it knows this without context.)

For these reasons, we decided against further investigating llama2

### Mistral

Next we tested Mistral 7 billion with 4 bit quantization requiring 4.1 GB disk storage. 
Right off the bat it performed much better without having to change the prompt in the slightest.
It correctly mentions it if the answer does not appear in the context but tries its best do answer the question still. With the very simple questions and contexts, we did not observe any hallucination. When a question can not be answered, but it is general knowledge, it answers correctly and specifies that it was not in the context. Also, Mistral did not add any weird formatting or hallucinated structure. All in all, it is very impressive for the small size and performs much better than llama2. It is also newer, which might be the reason. See the following examples:

Prompt, context, questions same as for llama2  
Answers: 
    - Based on the given context, Jesse's favorite color is red. The context does not provide any information about Jesse's preference for orange.
    - Theo's favorite color is not mentioned in the provided context.
    - Yes, penguins are birds. The context provided does not affect the answer to this question.

### Gemma

At the time of writing this, Google's Gemini-based open-source Gemma model has been released for 13 hours. There are two versions, a 7 billion and 2 billion parameter model. We tested the 4 bit quantized 7 billion parameter model. Again, without changing the prompt, context or questions, the answering performance appeared worse than with Mistral. The paper for Google Gemma stresses the model's performance being especially strong on coding and mathematical tasks compared to models of a similar size. In free recall question answering tasks (MMLU) it is comparable to Llama2 or Mistral. However, there is no benchmark on RAG and question answering with provided context. In our tests, it blatantly ignored the instruction to answer to the best of its ability if the answer is not contained within the context. Fiddling with the temperature only made answers worse. Here are the examples:

Prompt, context, questions same as for llama2  
Answers: 
    - The provided text does not specify whether Jesse's favorite color is orange or not, therefore I cannot answer the query. (Worse than Mistral. It should have extracted red as favorite color.)
    - The text does not provide information about Theo's favorite color, therefore I cannot answer this query. (Good)
    - I do not have any relevant context to answer the question of whether penguins are birds or not, therefore I cannot provide an answer. (It should answer similar to Mistral)
