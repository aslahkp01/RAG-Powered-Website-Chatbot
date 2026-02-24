# RAG-Powered Website Chatbot

A production-oriented Retrieval-Augmented Generation (RAG) chatbot that crawls a website and answers questions strictly from indexed website content.

## Current Features

- FastAPI backend with REST endpoints for indexing and chat
- React + Vite frontend with modern chat UI
- Dark/Light theme toggle with saved preference (localStorage)
- Recursive internal-link crawler with page/depth limits
- FAISS vector store + MMR retrieval for relevant context
- Groq LLM answering with strict RAG grounding prompt
- Local dev script to start backend and frontend together
- Frontend API proxy in Vite to avoid dev CORS fetch errors

## Project Structure

```text
backend/
  main.py         # FastAPI app and API routes
  config.py       # Environment/config values
  crawler.py      # Recursive crawler and text extraction
  vectorstore.py  # Chunking + embeddings + FAISS
  retriever.py    # Retrieval strategy
  llm.py          # Groq answer generation

frontend/
  src/App.jsx     # Main UI and API calls
  src/styles.css  # Modern + dark mode styles
  vite.config.js  # Dev proxy config

start-dev.ps1     # Starts backend + frontend locally (Windows)
requirements.txt
```

## API Endpoints

- `GET /api/health` → service health
- `POST /api/index` → crawl + index website URL
- `POST /api/chat` → ask question against indexed session

## Environment Variables

Create a `.env` file in project root:

```env
GROQ_API_KEY=your_key_here
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Optional frontend env in `frontend/.env`:

```env
VITE_API_BASE=http://127.0.0.1:8000
```

If `VITE_API_BASE` is not set, frontend uses relative `/api` and Vite proxy in dev.

## Run Locally

### Option 1: One command (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

### Option 2: Manual

Backend:

```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Build Frontend

```bash
cd frontend
npm run build
```

## Known Limitations

- JavaScript-heavy websites may require browser automation for full rendering.
- Some anti-bot protected websites may block crawling.
