import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "";

const apiUrl = (path) => `${API_BASE}${path}`;

export default function App() {
  const [url, setUrl] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "light");

  const isIndexed = useMemo(() => Boolean(sessionId), [sessionId]);

  useEffect(() => {
    document.body.classList.toggle("theme-dark", theme === "dark");
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((currentTheme) => (currentTheme === "dark" ? "light" : "dark"));
  };

  const handleIndex = async (event) => {
    event.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError("");
    setStatus("Crawling and indexing website...");

    try {
      const response = await fetch(apiUrl("/api/index"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to index website.");
      }

      setSessionId(data.session_id);
      setChatHistory([]);
      setStatus(
        `Indexed ${data.pages_crawled} page(s) and created ${data.chunks_created} chunk(s).`
      );
    } catch (err) {
      setError(err.message || "Unexpected error while indexing.");
      setStatus("");
      setSessionId("");
      setChatHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async (event) => {
    event.preventDefault();
    if (!question.trim() || !sessionId) return;

    const userQuestion = question.trim();
    setQuestion("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch(apiUrl("/api/chat"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, question: userQuestion }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to get answer.");
      }

      setChatHistory(data.history || []);
    } catch (err) {
      setError(err.message || "Unexpected error while asking question.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container">
      <header className="hero">
        <div className="heroTop">
          <p className="badge">AI-Powered Web Intelligence</p>
          <button className="toggleBtn" type="button" onClick={toggleTheme}>
            {theme === "dark" ? "☀ Light" : "🌙 Dark"}
          </button>
        </div>
        <h1>RAG Website Chatbot</h1>
        <p className="subtext">Index any website and ask grounded questions from its content.</p>
      </header>

      <form className="card" onSubmit={handleIndex}>
        <label className="label" htmlFor="url">Website URL</label>
        <div className="row">
          <input
            id="url"
            type="url"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
            disabled={loading}
          />
          <button className="primaryBtn" type="submit" disabled={loading}>
            {loading ? "Working..." : "Index"}
          </button>
        </div>
      </form>

      {status && <p className="status notice">{status}</p>}
      {error && <p className="error notice">{error}</p>}

      <section className="card">
        <div className="chatHeader">
          <h2>Chat</h2>
          <span className={isIndexed ? "state online" : "state offline"}>
            {isIndexed ? "Indexed" : "Not Indexed"}
          </span>
        </div>
        <div className="chatBox">
          {chatHistory.length === 0 ? (
            <p className="muted">
              {isIndexed
                ? "Ask your first question about the indexed site."
                : "Index a website first."}
            </p>
          ) : (
            chatHistory.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`msgWrap ${message.role}`}>
                <div className={`msg ${message.role}`}>
                  <strong>{message.role === "user" ? "You" : "Assistant"}</strong>
                  <p>{message.content}</p>
                </div>
              </div>
            ))
          )}
        </div>

        <form className="row askRow" onSubmit={handleAsk}>
          <input
            type="text"
            placeholder="Ask a question about the website..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={!isIndexed || loading}
            required
          />
          <button className="primaryBtn" type="submit" disabled={!isIndexed || loading}>
            Send
          </button>
        </form>
      </section>
    </main>
  );
}
