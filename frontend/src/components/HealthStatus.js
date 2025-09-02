import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./HealthStatus.css";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

export default function HealthStatus() {
  const navigate = useNavigate();

  const [providers, setProviders] = useState([]); // [{id, name}]
  const [loadingProviders, setLoadingProviders] = useState(true);
  const [loadError, setLoadError] = useState("");

  const [selection, setSelection] = useState(""); // "auto" | "gemini" | ...
  const [keys, setKeys] = useState({}); // { gemini: "KEY", openai: "KEY", ... }
  const [submitting, setSubmitting] = useState(false);
  const [health, setHealth] = useState(null); // { provider: [{name,status}], uptime }
  const [healthError, setHealthError] = useState("");

  // Load provider list on mount
  useEffect(() => {
    const fetchProviders = async () => {
      try {
        const res = await axios.get(`${API_BASE}/list`);
        // Expect: { providers: [{id, name}] }
        setProviders(res.data?.providers || []);
      } catch (err) {
        setLoadError(err.response?.data?.detail || "Failed to load providers.");
      } finally {
        setLoadingProviders(false);
      }
    };
    fetchProviders();
  }, []);

  // Providers to request keys for based on selection
  const requiredKeyNames = useMemo(() => {
    const names = providers.map((p) => p.name);
    if (!names.length) return [];

    if (!selection) return [];
    if (selection === "auto") {
      // All providers except 'auto'
      return names.filter((n) => n !== "auto");
    }
    // Only the selected provider
    return [selection];
  }, [providers, selection]);

  // Build payload for /health
  const apiKeysPayload = useMemo(() => {
    const list = requiredKeyNames
      .map((name) => ({
        name,
        api_key: (keys[name] || "").trim(),
      }))
      .filter((x) => x.api_key !== "");
    return { providers: list };
  }, [requiredKeyNames, keys]);

  const allRequiredKeysPresent =
    requiredKeyNames.length > 0 &&
    requiredKeyNames.every((name) => (keys[name] || "").trim().length > 0);

  const handleKeyChange = (name, value) => {
    setKeys((prev) => ({ ...prev, [name]: value }));
  };

  const runHealthCheck = async () => {
    setHealthError("");
    setHealth(null);

    if (!selection) {
      setHealthError("Please select a provider.");
      return;
    }
    if (!allRequiredKeysPresent) {
      setHealthError("Please enter all required API keys.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await axios.post(`${API_BASE}/health`, apiKeysPayload);
      setHealth(res.data);
    } catch (err) {
      setHealthError(err.response?.data?.detail || "Health check failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const isHealthy =
    health?.provider?.length &&
    health.provider.every((p) => p.status === true);

  const goToChat = () => {
    // Build api_keys array in the format your /chat expects
    // {
    //   "api_keys": [{ "name": "gemini", "api_key": "..." }],
    //   ...
    // }
    const api_keys = requiredKeyNames.map((name) => ({
      name,
      api_key: (keys[name] || "").trim(),
    }));

    navigate("/chat", {
      state: {
        provider: selection || "auto",
        apiKeys: api_keys,
      },
    });
  };

  return (
    <div className="prov-container">
      <header className="prov-header">
        <div className="prov-title">
          <h1>Provider Setup</h1>
          <p>Choose a provider and verify API access before chatting.</p>
        </div>
      </header>

      <section className="prov-card">
        <h2 className="section-title">Provider</h2>
        {loadingProviders ? (
          <div className="loading-row">Loading providers…</div>
        ) : loadError ? (
          <div className="error-banner">{loadError}</div>
        ) : (
          <div className="radio-row">
            {providers.map((p) => (
              <label key={p.id} className="radio-item">
                <input
                  type="radio"
                  name="provider"
                  value={p.name}
                  checked={selection === p.name}
                  onChange={(e) => {
                    setSelection(e.target.value);
                    setHealth(null);
                    setHealthError("");
                  }}
                />
                <span className="radio-label">{p.name}</span>
              </label>
            ))}
          </div>
        )}
      </section>

      {!!requiredKeyNames.length && (
        <section className="prov-card">
          <h2 className="section-title">API Keys</h2>
          <div className="keys-grid">
            {requiredKeyNames.map((name) => (
              <div className="key-field" key={name}>
                <label className="key-label">{name} API Key</label>
                <input
                  className="key-input"
                  type="password"
                  placeholder={`Enter ${name} API key`}
                  value={keys[name] || ""}
                  onChange={(e) => handleKeyChange(name, e.target.value)}
                />
              </div>
            ))}
          </div>

          <div className="actions">
            <button
              className="btn secondary"
              onClick={() => {
                // Clear keys for current selection
                const copy = { ...keys };
                requiredKeyNames.forEach((n) => delete copy[n]);
                setKeys(copy);
                setHealth(null);
                setHealthError("");
              }}
              disabled={submitting}
            >
              Clear
            </button>

            <button
              className="btn primary"
              onClick={runHealthCheck}
              disabled={!allRequiredKeysPresent || submitting}
            >
              {submitting ? "Checking..." : "Check Health"}
            </button>
          </div>

          {healthError && <div className="error-banner">{healthError}</div>}

          {health && (
            <div className="health-panel">
              <div className="health-summary">
                <span className={`dot ${isHealthy ? "ok" : "bad"}`} />
                <span className="health-text">
                  {isHealthy ? "Healthy" : "Unhealthy"}
                </span>
                <span className="muted">• Uptime {health.uptime}</span>
              </div>

              <div className="health-list">
                {health.provider.map((p) => (
                  <div key={p.name} className="health-item">
                    <span className="prov-name">{p.name}</span>
                    <span className={`badge ${p.status ? "good" : "warn"}`}>
                      {p.status ? "OK" : "Fail"}
                    </span>
                  </div>
                ))}
              </div>

              <div className="proceed">
                <button
                  className="btn proceed-btn"
                  onClick={goToChat}
                  disabled={!isHealthy}
                >
                  Continue to Chat
                </button>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
