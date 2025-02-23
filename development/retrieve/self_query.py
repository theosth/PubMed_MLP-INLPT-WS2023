import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from langchain.retrievers import SelfQueryRetriever
from langchain_community.llms import Ollama
from langchain_community.vectorstores.opensearch_vector_search import OpenSearchVectorSearch
from langchain.retrievers.self_query.opensearch import OpenSearchTranslator
from langchain.chains.query_constructor.base import (
    AttributeInfo,
)

metadata_field_info = [
    # AttributeInfo(
    #     name="pmid",
    #     description="The PubMed ID of the article",
    #     type="string",
    # ),
    # AttributeInfo(
    #     name="doi",
    #     description="The Digital Object Identifier of the article",
    #     type="string",
    # ),
    AttributeInfo(
        name="title",
        description="The title of the article",
        type="string",
    ),  
    AttributeInfo(
        name="publication_date",
        description="The year the article was published.",
        type="year",
    ),
]

document_content_description = "Abstract of a scientific article"

class FilterReturner(OpenSearchVectorSearch):
    def __init__(self):
        pass 

    def _remove_dot_metadata_and_keyword_from_keys(self, d):
        new_dict = {}
        for k, v in d.items():
            new_key = k.replace("metadata.", "").replace(".keyword", "")
            
            if isinstance(v, dict):
                new_dict[new_key] = self._remove_dot_metadata_and_keyword_from_keys(v)
            else:
                new_dict[new_key] = v
        return new_dict

    def search(self, query, search_type, **kwargs):
        """Returns filters provided by the SelfQueryRetriever.
        This is done in order to use the SelfQueryRetriever as 
        framework with minimal implementation even though this might seem very confusing.
        As a result. The `get_relevant_documents` method of the SelfQueryRetriever 
        returns *filters* not *documents*.
        """
        if self.remove_dot_metadata_from_keys:
            return self._remove_dot_metadata_and_keyword_from_keys(kwargs)
        return kwargs


def get_filters(query: str, remove_dot_metadata_from_keys=True) -> dict:
    underlying_llm = "mistral"
    llm = Ollama(
        model=underlying_llm,
        temperature = 0.3,
    )

    vectorstore = FilterReturner() # returns filters instead of documents
    vectorstore.remove_dot_metadata_from_keys = remove_dot_metadata_from_keys

    retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        document_contents=document_content_description,
        vectorstore=vectorstore,
        structured_query_translator=OpenSearchTranslator(),
        metadata_field_info=metadata_field_info,
    )

    try:
        filters = retriever.get_relevant_documents(query) # RETURNS FILTERS (see FilterReturner)
    except Exception as e:
        filters = {}

    if filters is None:
        filters = {}

    return filters

