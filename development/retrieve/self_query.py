import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))


from langchain.retrievers import SelfQueryRetriever
from langchain_community.llms import Ollama
# from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.vectorstores.opensearch_vector_search import OpenSearchVectorSearch
from langchain_core.vectorstores import VectorStore
from langchain.retrievers.self_query.opensearch import OpenSearchTranslator
from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    AttributeInfo,
    get_query_constructor_prompt,
)

metadata_field_info = [
    AttributeInfo(
        name="pmid",
        description="The PubMed ID of the article",
        type="string",
    ),
    AttributeInfo(
        name="doi",
        description="The Digital Object Identifier of the article",
        type="string",
    ),
    AttributeInfo(
        name="title",
        description="The title of the article",
        type="string",
    ),
    # AttributeInfo(
    #     name="author_list",
    #     description="List of authors of the article",
    #     type="list[string]",
    # ),
]
document_content_description = "Summary of a scientific article"

underlying_llm = "llama2"
llm = Ollama(
    model=underlying_llm,
    # temperature = 0,
    # repeat_penalty = 1.1,
)

prompt = get_query_constructor_prompt(
    document_content_description,
    metadata_field_info,
)
output_parser = StructuredQueryOutputParser.from_components()
query_constructor = prompt | llm | output_parser

class CustomOpensearchVectorstore(OpenSearchVectorSearch):
    def __init__(self):
        pass

    def search(self, query, search_type, **kwargs):
        print(kwargs)
        return [
            {
                "id": "1",
                "score": 0.9,
                "text": "The quick brown fox jumps over the lazy dog"
            }
        ]

# Create a retriever
retriever = SelfQueryRetriever(
    query_constructor=query_constructor,
    vectorstore=CustomOpensearchVectorstore(),
    verbose=True,
    structured_query_translator=OpenSearchTranslator(),
)


# SelfQueryRetriever.from_llm(
#     llm=llm,
#     vectorstore=,
    
# )

retriever.get_relevant_documents("articles with 'schizophrenia' in the title published after 2010")
