import os
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

# ================= CONFIG =================

load_dotenv()
os.environ["USER_AGENT"] = "Mozilla/5.0"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

MAX_DEPTH = 2
MAX_PAGES = 15

# ================= CRAWLER =================

def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    return " ".join(text.split())


def extract_links(url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        full_url = urljoin(url, a["href"])
        parsed = urlparse(full_url)
        base = urlparse(url)

        # Same domain only
        if parsed.netloc == base.netloc:
            links.append(full_url)

    return links


def crawl(url, depth=0, visited=None):
    if visited is None:
        visited = set()

    if depth > MAX_DEPTH or len(visited) >= MAX_PAGES:
        return []

    try:
        response = requests.get(url, timeout=5)
        html = response.text
    except:
        return []

    visited.add(url)

    text = clean_text(html)
    pages = [text]

    if depth < MAX_DEPTH:
        links = extract_links(url, html)
        for link in links:
            if link not in visited and len(visited) < MAX_PAGES:
                pages.extend(crawl(link, depth + 1, visited))

    return pages


# ================= VECTOR STORE =================

@st.cache_resource
def build_vector_store(url):
    with st.spinner("🔍 Crawling website..."):
        pages = crawl(url)

    documents = [Document(page_content=page) for page in pages]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    split_docs = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(split_docs, embeddings)

    return vector_store, len(pages), len(split_docs)


# ================= LLM =================

def generate_answer(question, context):
    prompt = f"""
You are an AI assistant.

Use ONLY the context below to answer.
If answer is not found, say:
"I don't know based on the provided content."

Keep answer concise (max 3 sentences).

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


# ================= STREAMLIT UI =================

st.set_page_config(page_title="Recursive RAG Web Chatbot", layout="wide")
st.title("🌐 Recursive RAG-Powered Website Chatbot")

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

url = st.text_input("Enter Website URL")

if url:
    try:
        vector_store, page_count, chunk_count = build_vector_store(url)
        st.session_state.vector_store = vector_store

        st.success(f"✅ Crawled {page_count} pages | Created {chunk_count} chunks")

    except Exception as e:
        st.error(f"Error: {e}")

question = st.chat_input("Ask a question about the website...")

if question and st.session_state.vector_store:
    st.chat_message("user").write(question)

    with st.spinner("🤖 Thinking..."):
        docs = st.session_state.vector_store.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])

        answer = generate_answer(question, context)

    st.chat_message("assistant").write(answer)