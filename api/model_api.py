import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from model import hf_misc
from api.model_api_connector import Question
from fastapi import FastAPI, HTTPException
import torch

app = FastAPI()

model, tokenizer = None, None


@app.on_event("startup")
async def load_model():
    global model, tokenizer
    # load the model and tokenizer
    # model, tokenizer = hf_misc.get_model_tokenizer("distilbert-base-uncased-distilled-squad")
    model, tokenizer = hf_misc.get_model_tokenizer("deepset/bert-base-cased-squad2")

@app.post("/question")
async def question_model(question: Question):
    # TODO: query e.g. opensearch to get the most relevant abstracts for the context 
    # for now some dummy context
    context = "The SARS-CoV-2 pandemic has led to a global shortage of personal protective equipment (PPE), including gowns, gloves, masks, and respirators. While PPE use is a key component of the hierarchy of controls recommended by CDC to protect healthcare workers from infectious pathogens such as SARS-CoV-2, PPE shortages during the pandemic have resulted in some healthcare workers resorting to the reuse of single-use PPE (e.g., surgical masks, N95 filtering facepiece respirators (FFRs)) for multiple encounters with patients but are intended for single use. This practice is referred to as “conventional capacity” strategies. In this study, we evaluated the decontamination and reuse of surgical masks and N95 FFRs using multiple decontamination methods."

    # get the answer from the model
    # ! This is just for demonstration purposes, to show how the api could be set up
    inputs = tokenizer.encode_plus(question.question, context, return_tensors="pt")
    outputs = model(**inputs)
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))

    # submit the response
    return {"answer": answer}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
