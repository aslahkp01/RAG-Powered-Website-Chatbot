import streamlit as st
from crawler import crawl
from vectorstore import build_vector_store
from retriever import retrieve_documents
from llm import generate_answer

st.set_page_config(page_title="Recursive RAG Web Chatbot", layout="wide")
st.title("🌐 Production-Level RAG Website Chatbot")

# Session state init
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "current_url" not in st.session_state:
    st.session_state.current_url = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

url = st.text_input("Enter Website URL")

# -------------------------------
# AUTO BUILD WHEN URL CHANGES
# -------------------------------

if url and url != st.session_state.current_url:
    st.session_state.vector_store = None
    st.session_state.chat_history = []
    st.session_state.current_url = url

    with st.spinner("🔍 Crawling and indexing website..."):
        documents = crawl(url)

        if not documents:
            st.error("❌ No content could be extracted from this website.")
        else:
            vector_store, chunk_count = build_vector_store(documents)
            st.session_state.vector_store = vector_store
            st.success(f"✅ Crawled {len(documents)} pages | Created {chunk_count} chunks")

# -------------------------------
# QUESTION HANDLING
# -------------------------------

question = st.chat_input("Ask a question about the website...")

if question and st.session_state.vector_store:
    st.session_state.chat_history.append(("user", question))

    with st.spinner("🤖 Thinking..."):
        docs = retrieve_documents(st.session_state.vector_store, question)
        context = "\n\n".join([doc.page_content for doc in docs])
        answer = generate_answer(question, context)

    st.session_state.chat_history.append(("assistant", answer))

# -------------------------------
# DISPLAY CHAT
# -------------------------------

for role, message in st.session_state.chat_history:
    st.chat_message(role).write(message)