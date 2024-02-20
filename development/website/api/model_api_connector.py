"""
This file contains the functions and types to call the model api.
If new Endpoints are added to the model api, the corresponding functions and types should be added here.
"""
import requests
import json
from pydantic import BaseModel


class Question(BaseModel):
    question: str


def ask_question(question: Question):
    url = "http://127.0.0.1:8000/question"
    headers = {"Content-Type": "application/json"}
    data = {"question": question.question}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"status_code": response.status_code, "detail": response.text}