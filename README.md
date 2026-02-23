📌 RAG-Powered Website Chatbot

A production-oriented Retrieval-Augmented Generation (RAG) chatbot that ingests any website URL, recursively crawls internal links, and answers user questions strictly based on the collected content.

🚀 Project Overview

This project allows users to:

Input any website URL

Automatically crawl and extract relevant content

Convert content into embeddings

Store them in a vector database

Ask questions grounded strictly in the scraped content

Receive hallucination-controlled answers

The system ensures minimal latency and robust handling of both structured and unstructured web data.

🏗 Architecture
User
  ↓
Frontend (Streamlit)
  ↓
Backend (Python)
  ↓
Crawler (Recursive)
  ↓
Text Cleaning & Chunking
  ↓
Embeddings
  ↓
Vector Database (FAISS)
  ↓
Retriever
  ↓
LLM (Groq)
  ↓
Grounded Response

🧠 Key Features
✅ Recursive Crawling

Crawls internal links up to configurable depth

Prevents duplicate visits

Respects max page limits

✅ Robust Content Extraction

Removes scripts and styles

Handles structured data (lists, tables)

Handles unstructured text (paragraphs)

✅ Strict RAG Grounding

Answers only from provided context

No external knowledge leakage

Controlled hallucination

Clear fallback when information is missing

✅ Anti-Bot Handling

Uses cloudscraper to bypass basic Cloudflare protection

Graceful error handling for blocked sites

✅ Performance Optimized

Configurable crawl depth

Configurable max pages

Low LLM temperature for stable responses

🛠 Tech Stack

- Python

- BeautifulSoup

- Cloudscraper

- LangChain

- FAISS(Vector DB)

- Groq LLM

- Streamlit (or React + FastAPI)

⚙️ Installation

git clone <your-repo-url>
cd project-folder
pip install -r requirements.txt

- Create a .env or configure:

GROQ_API_KEY=your_key_here

- Run:

streamlit run app.py

🔬 Evaluation Methodology

The chatbot was evaluated using the following criteria:

1️⃣ URL Ingestion

Tested with:

Static websites

Corporate websites

Documentation websites

Result: Successfully extracted content in most cases.

2️⃣ Recursive Crawling

Verified multiple internal pages were indexed.

Confirmed by tracking unique visited URLs.

3️⃣ Hallucination Control

Test Queries:

Relevant question → Answered correctly

Unrelated question → Proper refusal

Greeting → Polite response

Example:

Q: Who is Elon Musk?
A: "I couldn't find that information in the website content."

4️⃣ Structured Data Handling

Tested on:

Lists

Service descriptions

Company metrics

Successfully retrieved numeric data and service offerings.

5️⃣ Latency

Average response time:

1–4 seconds (depending on crawl size)

⚠️ Known Limitations

JavaScript-heavy websites may not fully render without browser automation.

Advanced bot-protected websites may block scraping.

Does not currently implement rate limiting.

📈 Future Improvements

Async crawling for faster indexing

Better semantic filtering of navigation content

Hybrid search (BM25 + Vector)

Caching embeddings

Frontend UI enhancement

Deployment with Docker

🎯 Why This Project Matters

This project demonstrates:

Practical RAG implementation

Real-world web crawling challenges

Hallucination mitigation

Vector search integration

Production-oriented architecture thinking

👤 Author

Muhammad Aslah
2026
