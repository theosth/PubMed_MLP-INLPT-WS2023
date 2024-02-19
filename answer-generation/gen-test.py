from langchain_community.llms import Ollama
import subprocess
import sys

subprocess.run("ollama pull llama2", shell=True, text=True,  stdout=sys.stdout, stderr=sys.stderr)
model = Ollama(model="llama2")

print(model.invoke("Tell me a math joke"))
print(model.invoke("Tell me a pyhsics joke"))
print(model.invoke("Tell me a computer science joke"))
print(model.invoke("Tell me a biology joke"))