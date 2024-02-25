from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
import langchain

from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains import LLMChain, StuffDocumentsChain
from langchain.prompts import PromptTemplate

from langchain_community.llms import Ollama
import subprocess
import sys
import ollama


class GenAI:
    prompt_templates = {
        "default": """
            Give just the answer to the following user query ```{query}``` using the information given in
            context ```{context}```.
            In the case there is no relevant information in the provided context,
            try to answer yourself, but tell the user that you did not have any
            relevant context to base your answer on. Be concise and factual.
            """,
        "yes_no": """
            Answer the following question ```{query}``` using the information given in
            context ```{context}```.
            In the case there is no relevant information in the provided context,
            try to answer yourself, but tell the user that you did not have any
            relevant context to base your answer on.
            Your answer to the question should consist only of one word, a simple yes or no. 
            """,
        "router": """Classify the following question as either a yes_no question or a factual question.
            Reply with only 'yes_no' or 'factual' depending on which it fits more. Limit the output to just this word.
            Question: ```{query}```""",
    }

    def __init__(self, underlying_llm="mistral"):
        if (
            len(
                [
                    model["name"]
                    for model in ollama.list()["models"]
                    if underlying_llm in model["name"]
                ]
            )
            == 0
        ):
            print("Pulling the model")
            subprocess.run(
                f"ollama pull {underlying_llm}",
                shell=True,
                text=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
        self.llm = Ollama(
            model=underlying_llm,
            # temperature = 0.01,
            # repeat_penalty = 1.1,
        )

        router_prompt = ChatPromptTemplate.from_template(
            self.prompt_templates["router"]
        )
        self.router_chain = LLMChain(llm=self.llm, prompt=router_prompt)

        prompt = ChatPromptTemplate.from_template(self.prompt_templates["default"])
        self.default_chain = create_stuff_documents_chain(self.llm, prompt)

        yes_no_prompt = ChatPromptTemplate.from_template(
            self.prompt_templates["yes_no"]
        )
        self.yes_no_chain = create_stuff_documents_chain(self.llm, yes_no_prompt)

    def invoke(self, context, query, withRouting=False):
        chain = self.default_chain

        if withRouting:
            output = self.router_chain.invoke({"query": query})
            questionType = output["text"].lower().strip()
            print(questionType)
            print(questionType == "yes_no")
            match questionType:
                case "yes_no":
                    print("Use yes-no chain")
                    chain = self.yes_no_chain
                case "factual":
                    print("Use factual chain")
                    chain = self.default_chain
                case _:
                    print("No match for question Type: ")
                    print(questionType)

        return chain.invoke({"context": context, "query": query})


test = GenAI()
test_docs = [
    Document(page_content="Jesse loves red but not yellow"),
    Document(page_content="Jamal loves green but not as much as he loves orange"),
    Document(page_content="Jesse's favorite color is red"),
]


langchain.debug = False

print("Invoke: \n")
print(test.invoke(test_docs, "Are penguins birds?", withRouting=True))
