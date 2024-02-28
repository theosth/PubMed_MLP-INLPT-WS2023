import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from development.commons import env

# load environment variables from .env file
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv(raise_error_if_not_found=True))
import os

os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_API_KEY")
import json
from langchain_community.document_loaders import JSONLoader

# for ragas
from ragas import evaluate
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context, conditional


def extract_metadata(record: dict, metadata: dict):
    # add all but the abstract to the metadata
    metadata.update({k: v for k, v in record.items() if k != "abstract"})
    # remove 'souce' and 'seq_num' from metadata
    metadata.pop("source", None)
    metadata.pop("seq_num", None)
    return metadata


data = JSONLoader(
    file_path=env.ABSTRACTS_DATASET_PATH,
    jq_schema=".documents[]",
    text_content=False,
    content_key="abstract",
    metadata_func=extract_metadata,
).load()

# limit to only 10 entries
data = data[:50]

print(len(data))
if len(data) > 50:
    print("data is too large, limiting to 10 entries")
    exit()

# create a testset generator
generator = TestsetGenerator.with_openai(
    generator_llm="gpt-3.5-turbo-16k", embeddings="text-embedding-ada-002", critic_llm="gpt-3.5-turbo-16k"
)
print("Generating testset...")
testset = generator.generate_with_langchain_docs(
    data, test_size=5, distributions={simple: 0.5, multi_context: 0.25, reasoning: 0.25}, with_debugging_logs=True
)
testset.to_pandas().to_json("ragas-testset.json", orient="records")