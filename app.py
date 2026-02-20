import os
import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from groq import Groq

# ------------------ CONFIG ------------------

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_api_key)

st.set_page_config(page_title="AI Web Crawler", layout="wide")
st.title("🌐 AI Web Crawler (RAG Powered)")

# ------------------ PROMPT TEMPLATE ------------------

def generate_answer(question, context):
    prompt = f"""
You are an intelligent AI assistant.

Use ONLY the context below to answer the question.
If the answer is not in the context, say:
"I don't know based on the provided content."

Keep the answer concise (max 3 sentences).

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": prompt}],
)

    return response.choices[0].message.content


# ------------------ LOAD + PROCESS WEBSITE ------------------

@st.cache_resource
def create_vector_store(url):
    loader = WebBaseLoader(url)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    docs = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(docs, embeddings)

    return vector_store


# ------------------ CHAT MEMORY ------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# ------------------ UI ------------------

url = st.text_input("🔗 Enter Website URL:")

vector_store = None

if url:
    try:
        with st.spinner("🔍 Crawling and indexing website..."):
            vector_store = create_vector_store(url)
        st.success("Website indexed successfully!")
    except Exception as e:
        st.error(f"Error loading website: {e}")

question = st.chat_input("Ask a question about the website...")

if question and vector_store:

    st.session_state.messages.append(("user", question))
    st.chat_message("user").write(question)

    with st.spinner("🤖 Thinking..."):
        docs = vector_store.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])

        answer = generate_answer(question, context)

    st.session_state.messages.append(("assistant", answer))
    st.chat_message("assistant").write(answer)