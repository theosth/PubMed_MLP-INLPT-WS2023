import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import streamlit as st
import development.retrieve.retrieval_wrapper as retrieve
# from streamlit_tags import st_tags, st_tags_sidebar


WEBSITE_TITLE = "Fluorite Q&A System"
OPTIONS_TITLE = "Options"
OPTION_PUBLICATION_YEAR_TITLE = "Publication Year"
OPTION_AUTHORS_TITLE = "Authors"
TIME_SPAN_MIN_YEAR = 2013
TIME_SPAN_MAX_YEAR = 2023
SOURCES_TITLE = "Sources"


def ask_opensearch(question: str):
    return retrieve.retrieve_abstracts(question)


def build_center():
    # Website Title
    st.title(WEBSITE_TITLE)

    # Initialize Conversation
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    # Reprint Conversation
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        message = ask_opensearch(prompt)
        st.session_state.last_sources = message
        st.session_state.messages.append({"role": "assistant", "content": "< missing answer >"})
        st.experimental_rerun()


def to_american_date_format(publication_date):
    parsed_date = datetime.strptime(publication_date, '%Y-%m-%d %H:%M:%S')
    return parsed_date.date()


def to_expander_titles(sources):
    return [f"{source.title}" for source in sources]


def build_upper_sidebar():
    # Options Sidebar Title
    st.sidebar.title(OPTIONS_TITLE)

    st.markdown("""
        <style>
        .stSlider [data-baseweb=slider]{
            width: 85%;
            margin-left: 7.5%;
            margin-top: 15px;
        }
        </style>
        """, unsafe_allow_html=True)

    # Time Span Selection
    time_span_start, time_span_end = st.sidebar.select_slider(
        OPTION_PUBLICATION_YEAR_TITLE,
        options=list(range(TIME_SPAN_MIN_YEAR, TIME_SPAN_MAX_YEAR + 1)),
        value=(TIME_SPAN_MIN_YEAR, TIME_SPAN_MAX_YEAR)
    )

    # Author Selection
    #keyword = st_tags_sidebar(
    #    label=OPTION_AUTHORS_TITLE,
    #    text='Enter Author Names...',
    #)


def truncate_for_expander(message, length):
    return f"{message[:length]}..."


def build_lower_sidebar():
    st.sidebar.title(SOURCES_TITLE)

    # Show Sources
    last_sources = st.session_state.get("last_sources")
    if last_sources is None:
        st.sidebar.write(":gray[Since there is no recent question, there are no sources so far! Don't be shy, ask our system!]")
    else:
        expander_titles = to_expander_titles(last_sources)
        for index, source in enumerate(last_sources):
            expander_title = expander_titles[index]
            content = f"({index + 1}) {expander_title}"
            with st.sidebar.expander(truncate_for_expander(content, 35)):
                st.write(f'<p><span style="font-weight:bold;">Title:</span> {source.title}</p>', unsafe_allow_html=True)
                st.write(f'<p><span style="font-weight:bold;">Authors:</span> {", ".join(source.author_list)}</p>', unsafe_allow_html=True)
                st.write(f'<p><span style="font-weight:bold;">Date:</span> {to_american_date_format(source.publication_date)}</p>', unsafe_allow_html=True)
                st.write(f'<p><span style="font-weight:bold;">Confidence:</span> ?</p>', unsafe_allow_html=True)


def build_sidebar():
    build_upper_sidebar()
    st.sidebar.divider()
    build_lower_sidebar()


if __name__ == "__main__":
    build_center()
    build_sidebar()
