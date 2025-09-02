<div align="center">

# Multi LLM Platform

**Enterprise LLM Orchestration Platform**  
Intelligently route requests across multiple AI providers with cost optimization and real-time monitoring.

</div>

---

This is an **enterprise-grade LLM orchestration platform** that routes requests across multiple AI providers (OpenAI, Anthropic, Google, local models), optimizing for **cost, speed, and quality**.

> _Think of it as the conductor of an AI orchestra—coordinating different AI models for the perfect performance._

---

## 🎯 Core Problems Solved

| Problem                    | Conductor Solution                                   |
| -------------------------- | ---------------------------------------------------- |
| 🔒 Vendor Lock-in          | Multi-provider architecture, easy switching          |
| 💰 Unpredictable Costs     | Free tier optimization, real-time cost tracking      |
| ⚡ Performance Variability | Intelligent routing based on request characteristics |
| 🔍 No Visibility           | Monitoring & analytics dashboard                     |
| 🛡️ Security Concerns       | Built-in governance & compliance features            |

---

## 🏗️ Architecture Overview

<!-- ![architechure](/images/architechure.png) -->

### 🧩 System Components

| Component        | Purpose            | Technology         |
| ---------------- | ------------------ | ------------------ |
| 🖥️ Web Dashboard | User Interface     | React + JavaScript |
| 🚀 API Gateway   | Request Handling   | FastAPI + Python   |
| 🧠 Smart Router  | Provider Selection | AI Logic + ML      |
| 🔌 LLM Providers | AI Model Access    | 4 Free APIs        |
| 💾 Database      | Data Storage       | PostgreSQL         |
| 📊 Analytics     | Monitoring         | Real-time Metrics  |

---

### Provider Selection Flow

| Criteria      | Provider  | Description              |
| ------------- | --------- | ------------------------ |
| Complex task? | Gemini 🧠 | Handles advanced queries |

---

### 🔄 Request Flow

1. **👤 User → API Request**
   - Authentication, Rate Limiting, Validation
2. **🧠 Smart Router → Analysis**
   - Request Complexity, Speed Requirements, Provider Health
3. **🤖 Provider Selection**
   - Gemini (Quality)
4. **📊 Response Processing**
   - Analytics Logging, Cost Tracking, Performance Metrics
5. **✅ Return to User**

---

### 💸 Cost Optimization Overview

| Provider       | Usage Bar | Allocation             |
| -------------- | --------- | ---------------------- |
| Gemini         | █████████ | 100% Free (60 req/min) |
| **Total Cost** |           | **$0.00/month**        |

---

## ✨ Key Features

### 🎯 Smart Routing Engine

- Automatic provider selection based on request type
- Performance optimization for speed, quality, or cost
- Fallback mechanisms for provider failover
- Custom routing rules

### 💰 Cost Optimization

- Maximizes free API quotas
- Real-time cost tracking
- Budget alerts
- ROI analytics

### 📊 Enterprise Monitoring

- Real-time dashboards
- Usage analytics
- Performance benchmarking
- Compliance reporting

### 🔌 Multi-Provider Support

- Google Gemini (quality, free tier)
- Easy extension for new providers

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose

### Requirements

- `fastapi`: FastAPI is the web framework that creates your REST API endpoints.
- `uvicorn[standard]`: Uvicorn is the ASGI server that runs your FastAPI application.
- `pydantic`:
  - Validates that users send correct data format
  - Automatically converts JSON ↔ Python objects
  - Generates interactive API docs,
  - Catches data errors before they cause problems
  - FastAPI can work without Pydantic, but you lose most of its benefits.
  - FastAPI is designed around Pydantic and works best with it.
- `python-dotenv`:
  - it's the easiest and most convenient way to manage environment variables during development.
- `google-generativeai`:
  - Google Generative AI is Google's official SDK for accessing Gemini AI models.
  - Connects to Google's Gemini AI models
  - Handles authentication with Google's servers
  - Provides easy-to-use Python interface
  - Manages API calls and responses
- `httpx`:
  - HTTPX is an async HTTP client for making API calls to external services.
  - good with fastAPI

### folder structure

```
conductor-llm-platform/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── providers/
│       ├── __init__.py
│       ├── base.py
│       └── gemini_provider.py
├── requirements.txt
├── .env
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

---

## End Points

<table>
   <thead>
      <tr>
         <th>Route</th>
         <th>Method</th>
         <th>Auth Required</th>
         <th>Purpose</th>
         <th>Status</th>
      </tr>
   </thead>
   <tbody>
      <tr>
         <td><code>/</code></td>
         <td>GET</td>
         <td>❌ No</td>
         <td>Welcome &amp; info</td>
         <td>✅ Always works</td>
      </tr>
      <tr>
         <td><code>/health</code></td>
         <td>GET</td>
         <td>❌ No</td>
         <td>Health check</td>
         <td>✅ Always works</td>
      </tr>
      <tr>
         <td><code>/docs</code></td>
         <td>GET</td>
         <td>❌ No</td>
         <td>API documentation</td>
         <td>✅ Always works</td>
      </tr>
      <tr>
         <td><code>/redoc</code></td>
         <td>GET</td>
         <td>❌ No</td>
         <td>Alt documentation</td>
         <td>✅ Always works</td>
      </tr>
      <tr>
         <td><code>/openapi.json</code></td>
         <td>GET</td>
         <td>❌ No</td>
         <td>OpenAPI schema</td>
         <td>✅ Always works</td>
      </tr>
      <tr>
         <td><code>/chat</code></td>
         <td>POST</td>
         <td>✅ Yes</td>
         <td>AI chat completion</td>
         <td>⚠️ Requires providers</td>
      </tr>
      <tr>
         <td><code>/status</code></td>
         <td>GET</td>
         <td>✅ Yes</td>
         <td>System metrics</td>
         <td>✅ Always works</td>
      </tr>
      <tr>
         <td><code>/providers</code></td>
         <td>GET</td>
         <td>✅ Yes</td>
         <td>Provider info</td>
         <td>✅ Always works</td>
      </tr>
   </tbody>
</table>
