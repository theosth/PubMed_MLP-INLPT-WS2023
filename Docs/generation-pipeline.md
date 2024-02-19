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