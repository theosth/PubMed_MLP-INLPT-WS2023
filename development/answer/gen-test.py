from langchain_community.llms import Ollama
import subprocess
import sys
import ollama

from langchain_community.chat_models import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

test_docs = [
    Document(page_content="Jesse loves red but not yellow"),
    Document(page_content = "Jamal loves green but not as much as he loves orange")
]

if 'llama' not in [model['details']['family'] for model in ollama.list()['models']]:
    print("Pulling the model")
    subprocess.run("ollama pull llama2", shell=True, text=True,  stdout=sys.stdout, stderr=sys.stderr)
llm = Ollama(
    model="llama2",
    #temperature = 0.01,
    repeat_penalty = 1.1,
)

prompt = ChatPromptTemplate.from_messages(
    [("system", "What are everyone's favorite colors:\n\n{context}")]
)
chain = create_stuff_documents_chain(llm, prompt)

print(chain.invoke({"context": test_docs}))
