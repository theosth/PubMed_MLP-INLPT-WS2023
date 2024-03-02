import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import development.retrieve.retrieval_wrapper as retrieve
import development.answer.answer_generation as answer
import streamlit as st

# --------------------[ Constant Definitions ]--------------------
# Website State Access
LATEST_SOURCES_KEY = "latest_sources"
SELF_QUERYING_TOGGLE_KEY = "self_querying_toggle"
LATEST_FILTERS_KEY = "latest_filters"

# Website Titles
WEBSITE_TITLE = "G2 Q&A System"
SELF_QUERYING_PARAMETERS_TITLE = "Self-Querying Parameters"
SELF_QUERYING_EXPANDER_TITLE = "Automatically Filtered Parameters"
LATEST_SOURCES_TITLE = "Sources"

# Notes
SELF_QUERYING_TOGGLE_NOTE = (":gray[Note: By enabling this option, the filtering parameters are automatically "
                             "extracted from the latest query. You cannot change them!]")
NO_RECENT_SOURCES_NOTE = (":gray[Since there is no recent question, there are no sources so far... Don't be shy, "
                          "ask our system!]")
EMPTY_SOURCES_NOTE = ":gray[No sources have been found for your latest query...]"
EMPTY_FILTERS_NOTE = ":gray[No filters could be extracted automagically from your latest query...]"

# Self-Querying Constraints
SELF_QUERYING_TIME_SPAN_MIN = 2013
SELF_QUERYING_TIME_SPAN_MAX = 2023

# Source View
PUBMED_ARTICLE_URL = "https://pubmed.ncbi.nlm.nih.gov"

# Answering
RETRIEVER = retrieve.CustomOpensearchAbstractRetriever()
GENAI = answer.GenAI()
# --------------------[ Constant Definitions ]--------------------


# --------------------[ Answering ]--------------------
def query_retriever(question: str):
    self_query_retrieval = st.session_state.get(SELF_QUERYING_TOGGLE_KEY)
    return RETRIEVER.get_relevant_documents(
        query=question,
        amount=3,
        self_query_retrieval=self_query_retrieval
    )


def prompt_model(retrieved_docs, question: str):
    return GENAI.invoke(context=retrieved_docs, query=question, withRouting=True)
# --------------------[ Answering ]--------------------


# --------------------[ Converters ]--------------------
def truncate_to_short_expander_title(message, length):
    return f"{message[:length]}..."


def to_source_expander_titles(sources):
    return [f"{source.title}" for source in sources]


def to_colored_confidence_rating(confidence_score):
    # Thresholds have been chosen empirically
    if confidence_score > 70:
        return f"<span style='color: #69B865;'>High</span>"
    elif confidence_score > 50:
        return f"<span style='color: #EDAE49;'>Medium</span>"
    else:
        return f"<span style='color: #D1495B;'>Low</span>"
# --------------------[ Converters ]--------------------


# --------------------[ Extractors ]--------------------
def extract_time_span_range(range_filter):
    publication_date_field = range_filter.get("publication_date")
    time_span_min = SELF_QUERYING_TIME_SPAN_MIN
    time_span_max = SELF_QUERYING_TIME_SPAN_MAX

    lt_filter = publication_date_field.get("lt")
    gt_filter = publication_date_field.get("gt")

    if lt_filter is not None:
        time_span_max = max(SELF_QUERYING_TIME_SPAN_MIN, min(int(lt_filter), time_span_max))

    if gt_filter is not None:
        time_span_min = min(SELF_QUERYING_TIME_SPAN_MAX, max(int(gt_filter), time_span_min))

    return time_span_min, time_span_max


def extract_exact_publication_date(exact_filter):
    publication_year = int(exact_filter.get("publication_date"))
    return publication_year, publication_year


def extract_time_span_from_filter(self_query):
    filter_field = self_query.get("filter")
    if filter_field is not None:
        # There exists a filter...
        range_filter_field = filter_field.get("range")
        if range_filter_field is not None:
            # ... and it has a range
            return extract_time_span_range(range_filter_field)

        exact_date_field = filter_field.get("term")
        if exact_date_field is not None:
            # ... and it has an exact date
            return extract_exact_publication_date(exact_date_field)

    return None, None


def extract_title_keywords_from_filter(self_query):
    filter_field = self_query.get("filter")
    if filter_field is not None:
        # There exists a filter...
        match_field = filter_field.get("match")
        if match_field is not None:
            title_field = match_field.get("title")
            return title_field

    return None


def extract_used_filters(abstracts):
    if len(abstracts) > 0:
        return abstracts[0].filters
    else:
        self_querying_enabled = st.session_state.get(SELF_QUERYING_TOGGLE_KEY)
        return {} if self_querying_enabled else None
# --------------------[ Extractors ]--------------------


# --------------------[ Website Components ]--------------------
def write_expander_url(keyword, content):
    st.write(
        f'<p><span style="font-weight:bold;">{keyword}:</span> <a href="{content}">{content}</a></p>',
        unsafe_allow_html=True,
    )


def write_expander_normal_entry(keyword, content):
    st.write(
        f'<p><span style="font-weight:bold;">{keyword}:</span> {content if content is not None else "-"}</p>',
        unsafe_allow_html=True,
    )


def write_self_querying_expander():
    latest_sources = st.session_state.get(LATEST_SOURCES_KEY)
    latest_filters = st.session_state.get(LATEST_FILTERS_KEY)
    if latest_filters is None:
        # Nothing to show...
        return
    if len(latest_filters) == 0 and len(latest_sources) > 0:
        # No filter could be extracted...
        st.sidebar.write(EMPTY_FILTERS_NOTE)
    else:
        # Filter could be extracted...
        time_span_min, time_span_max = extract_time_span_from_filter(latest_filters)
        title = extract_title_keywords_from_filter(latest_filters)

        if time_span_min is not None and time_span_max is not None:
            if time_span_min == time_span_max:
                write_expander_normal_entry("Year", f"{time_span_min}")
            else:
                write_expander_normal_entry("Timespan", f"{time_span_min} - {time_span_max}")

        if title is not None:
            write_expander_normal_entry("Title Keywords", title)


def write_source_expander(source):
    write_expander_url("URL", f"{PUBMED_ARTICLE_URL}/{source.pmid}/")
    write_expander_normal_entry("Title", source.title)
    write_expander_normal_entry("PMID", source.pmid)
    write_expander_normal_entry("Authors", ", ".join(source.author_list))
    write_expander_normal_entry("Publication Date", source.publication_date)
    write_expander_normal_entry("Confidence", to_colored_confidence_rating(source.confidence))
# --------------------[ Website Components ]--------------------


# --------------------[ Website Construction ]--------------------
def build_chat():
    # Website Title
    st.title(WEBSITE_TITLE)

    # Initialize Conversation
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    if prompt := st.chat_input():
        # Asking Question
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        # Thinking...
        retrieved_langchain_documents = query_retriever(prompt)
        abstracts = retrieve.convert_langchain_documents_to_abstracts(retrieved_langchain_documents)
        st.session_state[LATEST_SOURCES_KEY] = abstracts

        # Extracting Filters
        st.session_state[LATEST_FILTERS_KEY] = extract_used_filters(abstracts)

        # Answering
        answer = prompt_model(
            retrieved_docs=retrieved_langchain_documents,
            question=prompt
        )

        st.session_state.messages.append({"role": "assistant", "content": answer})

    # Reprint Conversation
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])


def build_upper_sidebar():
    # Self-Querying Parameters Sidebar Title
    st.sidebar.title(SELF_QUERYING_PARAMETERS_TITLE)

    # Self-Querying Toggle
    toggled = st.sidebar.toggle(SELF_QUERYING_TOGGLE_NOTE)
    st.session_state[SELF_QUERYING_TOGGLE_KEY] = toggled
    if toggled:
        with st.sidebar.expander(SELF_QUERYING_EXPANDER_TITLE):
            write_self_querying_expander()


def build_lower_sidebar():
    st.sidebar.title(LATEST_SOURCES_TITLE)

    # Show Sources
    last_sources = st.session_state.get(LATEST_SOURCES_KEY)
    if last_sources is None:
        st.sidebar.write(NO_RECENT_SOURCES_NOTE)
    elif len(last_sources) == 0:
        st.sidebar.write(EMPTY_SOURCES_NOTE)
    else:
        expander_titles = to_source_expander_titles(last_sources)
        for index, source in enumerate(last_sources):
            expander_title = expander_titles[index]
            content = f"({index + 1}) {expander_title}"

            # Create Source Expander
            with st.sidebar.expander(truncate_to_short_expander_title(content, 35)):
                write_source_expander(source)


def build_sidebar():
    build_upper_sidebar()
    st.sidebar.divider()
    build_lower_sidebar()
# --------------------[ Website Construction ]--------------------


if __name__ == "__main__":
    build_chat()
    build_sidebar()
