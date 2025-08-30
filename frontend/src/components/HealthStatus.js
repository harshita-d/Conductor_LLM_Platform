// HealthStatus.js
import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./HealthStatus.css";

const HealthStatus = () => {
  const [apiKey, setApiKey] = useState("");
  const [healthData, setHealthData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const checkHealth = async () => {
    setError("");
    setHealthData(null);

    if (!apiKey.trim()) {
      setError("Please enter a valid API key.");
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post("http://localhost:8000/health", {
        providers: [{ name: "gemini", api_key: apiKey }],
      });

      setHealthData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Health check failed.");
    } finally {
      setLoading(false);
    }
  };

  const isHealthy = healthData?.provider?.[0]?.status === true;

  return (
    <div className="health-container">
      <h2 className="title">Gemini Health Check</h2>

      <input
        type="text"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        placeholder="Enter your Gemini API Key"
        className="input"
      />

      <button onClick={checkHealth} disabled={loading} className="check-button">
        {loading ? "Checking..." : "Check Health"}
      </button>

      {error && <p className="error-msg">{error}</p>}

      {healthData && (
        <div className="result-card">
          <h3>Health Status</h3>
          <p>
            <strong>Provider:</strong> {healthData.provider[0].name}
          </p>
          <p>
            <strong>Status:</strong>{" "}
            <span className={isHealthy ? "status-healthy" : "status-unhealthy"}>
              {isHealthy ? "Healthy" : "Unhealthy"}
            </span>
          </p>
          <p>
            <strong>Uptime:</strong> {healthData.uptime}
          </p>

          <button
            onClick={() => navigate("/chat", { state: { apiKey } })}
            disabled={!isHealthy}
            className={`goto-chat-button ${isHealthy ? "" : "disabled"}`}
          >
            Go to Chat
          </button>
        </div>
      )}
    </div>
  );
};

export default HealthStatus;
