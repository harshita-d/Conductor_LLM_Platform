// ChatScreen.js
import React, { useEffect, useMemo, useRef, useState, useCallback } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";
import "./ChatScreen.css";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

const ChatScreen = () => {
  const { state } = useLocation();
  const navigate = useNavigate();
  const apiKey = state?.apiKey || "";

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]); // [{role:"user"|"assistant", content:string}]
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [maxTokens, setMaxTokens] = useState(100);
  const [temperature, setTemperature] = useState(0.8);

  const [status, setStatus] = useState(null); // server status payload
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  const providerHealthy = useMemo(
    () => Boolean(status?.providers?.[0]?.healthy),
    [status]
  );

  // Redirect back if no API key present
  useEffect(() => {
    if (!apiKey) navigate("/");
  }, [apiKey, navigate]);

  // Fetch provider/system status on mount
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const res = await axios.get(`${API_BASE}/status`);
        if (active) setStatus(res.data);
      } catch {
        // Keep quiet; UI handles lack of status gracefully
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  // Always scroll to last message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const handleSend = useCallback(async () => {
    if (!input.trim() || loading) return;

    setError("");
    const userMsg = { role: "user", content: input.trim() };
    const history = [...messages, userMsg];

    setMessages(history);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        api_keys: [{ name: "gemini", api_key: apiKey }],
        max_tokens: Number(maxTokens),
        temperature: Number(temperature),
        message: history, // full history per your backend contract
        provider: "auto",
      });

      const reply = res.data?.response || "No response";
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to get response.";
      setError(detail);
      // Echo error as assistant bubble for visibility
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${detail}` },
      ]);
    } finally {
      setLoading(false);
      // refocus input for fast follow-ups
      inputRef.current?.focus();
    }
  }, [apiKey, input, loading, maxTokens, messages, temperature]);

  // Enter to send, Shift+Enter for newline
  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError("");
    inputRef.current?.focus();
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <header className="chat-header">
        <div className="chat-title">
          <h2>Gemini Chat</h2>
          <span
            className={`health-dot ${
              providerHealthy ? "ok" : "bad"
            }`}
            title={providerHealthy ? "Healthy" : "Unhealthy"}
          />
        </div>
        <div className="header-actions">
          <button className="ghost-btn" onClick={() => navigate("/")}>
            Back
          </button>
          <button className="ghost-btn" onClick={clearChat} disabled={loading}>
            Clear
          </button>
        </div>
      </header>

      {/* Status strip (optional, collapsible look) */}
      <section className="status-card">
        <div className="status-row">
          <div>
            <span className="label">Status</span>
            <span className={`badge ${providerHealthy ? "good" : "warn"}`}>
              {providerHealthy ? "Healthy" : "Unhealthy"}
            </span>
          </div>
          <div>
            <span className="label">Uptime</span>
            <span className="value">{status?.uptime ?? "—"}</span>
          </div>
          <div>
            <span className="label">Total Requests</span>
            <span className="value">{status?.total_requests ?? 0}</span>
          </div>
        </div>
      </section>

      {/* Controls */}
      <section className="controls">
        <div className="control">
          <label htmlFor="tokens">Max tokens</label>
          <input
            id="tokens"
            type="number"
            min={1}
            value={maxTokens}
            onChange={(e) => setMaxTokens(parseInt(e.target.value || "1", 10))}
            className="input-field"
          />
        </div>
        <div className="control">
          <label htmlFor="temp">Temperature</label>
          <input
            id="temp"
            type="number"
            step="0.1"
            min={0}
            max={1}
            value={temperature}
            onChange={(e) =>
              setTemperature(parseFloat(e.target.value || "0"))
            }
            className="input-field"
          />
        </div>
      </section>

      {/* Chat transcript */}
      <main className="chat-box">
        {messages.length === 0 && (
          <div className="empty-hint">
            Start a conversation… (Enter to send, Shift+Enter for newline)
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={`${m.role}-${i}`}
            className={`chat-bubble ${m.role === "user" ? "user" : "assistant"}`}
          >
            {m.content}
          </div>
        ))}

        {loading && (
          <div className="chat-bubble assistant">
            <span className="typing">
              <span />
              <span />
              <span />
            </span>
          </div>
        )}
        <div ref={chatEndRef} />
      </main>

      {/* Composer */}
      <footer className="chat-input">
        <textarea
          ref={inputRef}
          className="input-field textarea"
          placeholder="Ask something…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          rows={1}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={loading || !input.trim() || !providerHealthy}
          title={!providerHealthy ? "Provider is unhealthy" : "Send"}
        >
          {loading ? "Sending…" : "Send"}
        </button>
      </footer>

      {error && <div className="error-text">{error}</div>}
    </div>
  );
};

export default ChatScreen;
