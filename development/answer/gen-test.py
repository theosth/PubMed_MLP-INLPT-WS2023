from langchain_community.llms import Ollama
import subprocess
import sys
import ollama

from langchain_community.chat_models import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

prompt_template =  """
Give just the answer to the following user query ```{query}``` using the information given in
context ```{context}```.
In the case there is no relevant information in the provided context,
try to answer yourself, but tell the user that you did not have any
relevant context to base your answer on. Be concise and factual. 
Answer just the question, do not provide any additional information.
"""

test_docs = [
    Document(page_content="Jesse loves red but not yellow"),
    Document(page_content = "Jamal loves green but not as much as he loves orange"),
    Document(page_content = "Jesse's favorite color is red"),
]

if 'llama' not in [model['details']['family'] for model in ollama.list()['models']]:
    print("Pulling the model")
    subprocess.run("ollama pull llama2", shell=True, text=True,  stdout=sys.stdout, stderr=sys.stderr)
llm = Ollama(
    model="llama2",
    temperature = 0.01,
    repeat_penalty = 1.1,
)

prompt = ChatPromptTemplate.from_template(prompt_template)
chain = create_stuff_documents_chain(llm, prompt)

print(chain.invoke({"context": test_docs, "query": "Is Jesse's favorite color orange?"}))
