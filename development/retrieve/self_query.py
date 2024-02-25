from langchain.retrievers import SelfQueryRetriever
from langchain_community.llms import Ollama
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.vectorstores import VectorStore
from langchain.retrievers.self_query.opensearch import OpenSearchTranslator
from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    AttributeInfo,
    get_query_constructor_prompt,
)

metadata_field_info = [
    AttributeInfo(
        name="genre",
        description="The genre of the movie. One of ['science fiction', 'comedy', 'drama', 'thriller', 'romance', 'action', 'animated']",
        type="string",
    ),
    AttributeInfo(
        name="year",
        description="The year the movie was released",
        type="integer",
    ),
    AttributeInfo(
        name="director",
        description="The name of the movie director",
        type="string",
    ),
    AttributeInfo(
        name="rating", description="A 1-10 rating for the movie", type="float"
    ),
]
document_content_description = "Brief summary of a movie"

underlying_llm = "mistral"
llm = Ollama(
    model=underlying_llm,
    # temperature = 0.01,
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
    structured_query_translator=OpenSearchTranslator(),
)

retriever.get_relevant_documents("movies from the year after 2000")