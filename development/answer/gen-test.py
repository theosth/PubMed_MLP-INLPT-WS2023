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
"""

test_docs = [
    Document(page_content="Jesse loves red but not yellow"),
    Document(page_content = "Jamal loves green but not as much as he loves orange"),
    Document(page_content = "Jesse's favorite color is red"),
]

if len([model['name'] for model in ollama.list()['models'] if 'gemma' in model['name']]) == 0:
    print("Pulling the model")
    subprocess.run("ollama pull llama2", shell=True, text=True,  stdout=sys.stdout, stderr=sys.stderr)
llm = Ollama(
    model="gemma",
    # temperature = 0.01,
    # repeat_penalty = 1.1,
)

prompt = ChatPromptTemplate.from_template(prompt_template)
chain = create_stuff_documents_chain(llm, prompt)

print(chain.invoke({"context": test_docs, "query": "Is Jesse's favorite color orange?"}))
print(chain.invoke({"context": test_docs, "query": "What is Theo's favorite color?"}))
print(chain.invoke({"context": test_docs, "query": "Are penguins birds?"}))
