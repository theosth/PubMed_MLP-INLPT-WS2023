import json
import development.commons.env as env


def is_short_last_fragment(document):
    return (
        document["fragment_id"] == document["number_of_fragments"] - 1
        and document["fragment_id"] != 0
        and len(document["abstract_fragment"].split()) < 50
    )


def find_document_by_id(abstract_id, fragment_id, documents):
    for doc in documents:
        if doc["pmid"] == abstract_id and doc["fragment_id"] == fragment_id:
            return doc
    raise "Error, document not found"
    return None


def analyseDocumentFragments():
    with open(env.ABSTRACT_FRAGMENT_DATASET_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    all_documents = data["documents"]
    total_number_documents = len(all_documents)

    print(total_number_documents)

    short_documents = list(filter(is_short_last_fragment, all_documents))

    print(len(short_documents))

    unnecessary_documents = []
    for document in short_documents:
        previous_fragment = find_document_by_id(
            document["pmid"], document["fragment_id"] - 1, all_documents
        )
        if document["abstract_fragment"] in previous_fragment["abstract_fragment"]:
            unnecessary_documents.append(document)

    print(len(unnecessary_documents))


analyseDocumentFragments()
