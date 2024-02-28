import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import json
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from development.retrieve.retrieval_wrapper import CustomOpensearchRetriever

llm = Ollama(
    model="mistral",
    temperature = 0,
    # repeat_penalty = 3,
)

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=CustomOpensearchRetriever(), verbose=True)

question = "What is the effect of COVID-19 on the human body?"
result = qa_chain.invoke({"query": question})
print(json.dumps(result, indent=2))
