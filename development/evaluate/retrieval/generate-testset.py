import json
import ijson
import random
from openai import OpenAI
import time
import os

# load environment variables from .env file
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv(raise_error_if_not_found=True))


def loadRandomDocuments(file_path, number_of_documents):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    documents = data['documents']
    total_documents = len(documents)
    print(total_documents)

    random_doc_indices = set()
    for _ in range(number_of_documents):
        random_number = random.randint(0, total_documents - 1)
        if random_number not in random_doc_indices:
            random_doc_indices.add(random_number)

    return list(map(lambda x: documents[x], list(random_doc_indices)))


def addQuestionToJson(questionObject, filename):
     # Load the existing JSON data
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Ensure that "documents" field exists
    if 'questions' not in data:
        data['questions'] = []

    # Add the new document to the "questions" array
    data['questions'].append(questionObject)

    # Write the updated data back to the file
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)
    

def promptChatGPT(prompt, apiClient):
    response = apiClient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content


def askYesNoQuestion(context, apiClient):
    return promptChatGPT(f"""Generate a question that can be answered with the context information delimited by triple backticks. The question should be answerable with a simple yes or no. Only use phrases that don't require context for the person reading the question, meaning you should not use references like 'in the study' or 'in the context' because the reader of the question doesn't have the context and therefore can not know which study is meant. Take everything written in the context as generally true statements, meaning there is no need to add phrases like 'in the text', 'in the context', 'in the study' or anything equivalent to this.
Limit the output to the generated question.
Context: ```{context}```""", apiClient)

def askFactualQuestion(context, apiClient):
    return promptChatGPT(f"""Generate a question that can be answered with the information delimited by triple backticks. The question should be answerable with specific factual information. This means not a yes/no question but a question where some short information is the answer. 
Take everything written in the context as generally true statements, meaning there is no need to add phrases like "in the text", "in the context", "in the study" or anything equivalent to this.
Limit the output to the generated question.
```${context}```
Remember to only use phrases that don't require context for the person reading the question, meaning you should not use references like "in the study" or "in the context" because the reader of the question doesn't have the context and therefore can not know which study is meant."""
, apiClient)



def validateQuestion(question):
    criticalPhrases = ['in the study', 'in the context', 'in the sample', 'in the text', 'in this', 'this study']
    for phrase in criticalPhrases:
        if phrase in question:
            return False

    return True

client = OpenAI(api_key = os.getenv("OPEN_API_KEY"))

numberOfQuestionsToBeGenerated = 500

validCounter = 0
needManualCheckCounter = 0

randomDocuments = loadRandomDocuments('../../fragment-dataset.json', numberOfQuestionsToBeGenerated)

for x in range(0,numberOfQuestionsToBeGenerated):
    # Randomly assign whether to ask yes/no or factual question
    isYesNoQuestion = random.randint(0, 1)
    doc = randomDocuments[x-1]
    if isYesNoQuestion:
        question = askYesNoQuestion(doc['abstract_fragment'], client)
    else:
        question = askFactualQuestion(doc['abstract_fragment'], client)
    print("Question "+str(x))
    print(question)
    isValid = validateQuestion(question)
    questionObject = {
        "question": question,
        "pmid": doc['pmid'],
        "fragment_id": doc['fragment_id'],
        "id": doc['id'],
        "question_type": "yes/no" if isYesNoQuestion else "factual"
    }
    if isValid:
        addQuestionToJson(questionObject, "retrieval-testset.json")
        validCounter += 1
    else:
        addQuestionToJson(questionObject, "questions-to-be-checked.json")
        needManualCheckCounter += 1

    # pause for 21 seconds to avoid issues with the api rate limit of 3 Requests per Minute
    print("Wait before sending next request")
    time.sleep(21)
