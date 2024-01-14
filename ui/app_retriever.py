import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import opensearch_connector as ops
import streamlit as st


def query_opensearch(question: str):
    query_simple_match = ops.create_simple_match_query(question)
    query_simple_neural = ops.create_neural_query(question)
    query_hybrid_multimatch_neural = ops.create_hybrid_multimatch_neural_query(
        query_text = question,
        match_on_fields = ['abstract_fragment', 'title', 'keyword_list']
    )
    response = ops.execute_query(
        query = query_hybrid_multimatch_neural, 
        pipeline_id = 'basic-nlp-search-pipeline',
        # index = 'abstracts',
        size=5,
        source_includes=['_id', 'fragment_id', 'title', 'abstract_fragment'] # Define which fields should be returned
    )
    hits = ops.extract_hits_from_response(response)
    print(hits)
    return hits
    

def get_answer(question):
    opensearch_results = query_opensearch(question)
    return opensearch_results


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
