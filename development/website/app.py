# To enable importing from other subfolders
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
# How we would later import the model api call function from the api folder
from development.legacy.model import pubMedModel
from development.website.api.model_api_connector import Question, ask_question

import streamlit as st
# from streamlit_chat import messages


def get_answer_from_HF_API_model(question):
    # some dummy stuff right now to test the UI and some HuggingFace stuff
    # for now some dummy context
    context = "The SARS-CoV-2 pandemic has led to a global shortage of personal protective equipment (PPE), including gowns, gloves, masks, and respirators. While PPE use is a key component of the hierarchy of controls recommended by CDC to protect healthcare workers from infectious pathogens such as SARS-CoV-2, PPE shortages during the pandemic have resulted in some healthcare workers resorting to the reuse of single-use PPE (e.g., surgical masks, N95 filtering facepiece respirators (FFRs)) for multiple encounters with patients but are intended for single use. This practice is referred to as “conventional capacity” strategies. In this study, we evaluated the decontamination and reuse of surgical masks and N95 FFRs using multiple decontamination methods."
    context="The Amazon rainforest (Portuguese: Floresta Amazônica or Amazônia; Spanish: Selva Amazónica, Amazonía or usually Amazonia; French: Forêt amazonienne; Dutch: Amazoneregenwoud), also known in English as Amazonia or the Amazon Jungle, is a moist broadleaf forest that covers most of the Amazon basin of South America. This basin encompasses 7,000,000 square kilometres (2,700,000 sq mi), of which 5,500,000 square kilometres (2,100,000 sq mi) are covered by the rainforest. This region includes territory belonging to nine nations. The majority of the forest is contained within Brazil, with 60% of the rainforest, followed by Peru with 13%, Colombia with 10%, and with minor amounts in Venezuela, Ecuador, Bolivia, Guyana, Suriname and French Guiana. States or departments in four nations contain Amazonas in their names. The Amazon represents over half of the planet's remaining rainforests, and comprises the largest and most biodiverse tract of tropical rainforest in the world, with an estimated 390 billion individual trees divided into 16,000 species."
    answer = pubMedModel.get_answer_from_model_DistilBertBaseQA(question, context)
    return answer

def get_answer(question):
    question = Question(question=question)
    answer = ask_question(question)
    return answer["answer"]


st.title("Question Answering System ") 

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        message = get_answer(prompt)
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.experimental_rerun()
