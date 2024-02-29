import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from development.commons import env


from langchain_core.language_models import BaseLanguageModel
from langchain_community.llms import Ollama
from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

# default extractor
from ragas.testset.extractor import KeyphraseExtractor
from langchain.text_splitter import TokenTextSplitter

# default DocumentStore
from ragas.testset.docstore import InMemoryDocumentStore
from sentence_transformers import SentenceTransformer

# make sure to wrap them with wrappers
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.testset.generator import TestsetGenerator




def get_local_TestsetGenerator(
    generator_llm_ollama_settings: dict = {
        "model": "mistral",
        "temperature": 0,
        "repeat_penalty": 1,
    },
    critic_llm_ollama_settings: dict = {
        "model": "mistral",
        "temperature": 0,
        "repeat_penalty": 1,
    },
    embedding_model_hf: str = "pritamdeka/S-PubMedBert-MS-MARCO",
    chunk_size: int = 512,
) -> TestsetGenerator:
    """
    # ! TODO: For some reason the following code is not working!
    # ! However, we keep it here for future reference.
    """

    generator_llm = Ollama(**generator_llm_ollama_settings)
    critic_llm = Ollama(**critic_llm_ollama_settings)
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_hf)

    # make sure to wrap them with wrappers
    generator_llm = LangchainLLMWrapper(generator_llm)
    critic_llm = LangchainLLMWrapper(critic_llm)
    embeddings = LangchainEmbeddingsWrapper(embeddings)

    # use to create in memory document store
    keyphrase_extractor = KeyphraseExtractor(llm=generator_llm)
    splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=0)

    docstore = InMemoryDocumentStore(
        splitter=splitter,
        embeddings=embeddings,
        extractor=keyphrase_extractor,
    )

    return TestsetGenerator(
        docstore=docstore,
        generator_llm=generator_llm,
        critic_llm=critic_llm,
        embeddings=embeddings,
    )


if __name__ == "__main__":
    testsetGenerator = get_local_TestsetGenerator()
