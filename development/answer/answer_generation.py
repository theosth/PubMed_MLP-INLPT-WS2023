from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_community.llms import Ollama
import subprocess
import sys
import ollama

class GenAI:
    prompt_template =  """
Give just the answer to the following user query ```{query}``` using the information given in
context ```{context}```.
In the case there is no relevant information in the provided context,
try to answer yourself, but tell the user that you did not have any
relevant context to base your answer on. Be concise and factual.
"""

    def __init__(self, underlying_llm = "mistral"):
        if len([model['name'] for model in ollama.list()['models'] if underlying_llm in model['name']]) == 0:
            print("Pulling the model")
            subprocess.run(f"ollama pull {underlying_llm}", shell=True, text=True,  stdout=sys.stdout, stderr=sys.stderr)
        self.llm = Ollama(
            model=underlying_llm,
            # temperature = 0.01,
            # repeat_penalty = 1.1,
        )

        self.prompt = ChatPromptTemplate.from_template(self.prompt_template)
        self.chain = create_stuff_documents_chain(self.llm, self.prompt)

    def invoke(self, context, query):
        return self.chain.invoke({"context": context, "query": query})