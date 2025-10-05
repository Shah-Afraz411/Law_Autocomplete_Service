# Law Autocomplete Service

> Intelligent, domain‑aware, real‑time autocomplete for legal search inputs (German / EU law–oriented, easily extendable to other domains).

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-🚀-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-frontend-ff4b4b.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Stage-Alpha-orange.svg)]()
[![Type hints](https://img.shields.io/badge/Typing-PEP%20484-informational.svg)]()

---

## ✨ Overview

The **Law Autocomplete Service** is a modular microservice that generates *contextual legal autocomplete suggestions* in real time—similar to a modern search engine experience.  
It supports:
- Legal domain bias (e.g., German BGB / Residence Act categories)
- Category tagging of suggestions
- Multi-language output (configurable)
- Pluggable LLM engine (Google Vertex AI Gemini) with graceful local mock fallback
- Streamlit real-time UI (no enter key or submit button needed)

Designed for integration into larger law, compliance, knowledge, or legal assistance platforms.

---

## 🧩 Key Features

| Feature | Description |
|---------|-------------|
| FastAPI Backend | Async API with clean response models |
| Real-Time Frontend | Streamlit app updates suggestions per keystroke (debounced) |
| LLM Integration | Google Vertex AI Gemini (configurable / optional) |
| Fallback Mode | Deterministic mock suggestions when LLM is disabled |
| Domain Categories | Category tagging + “Other (Misc.)” normalization |
| Localization | Output language hint (EN, DE, FR, ES, IT configurable) |
| Expandable | Clear service layer & prompt abstraction |
| Singleton Model | Loads once; warmed on startup |
| Debounced Requests | Reduces LLM spend & latency amplification |
| Extensible Architecture | Prompts, schemas, services separated |
| Dockerized | Backend & frontend containers |
| Test Scaffold | Pytest async example included |

---

## 🏗️ Architecture

```
+-------------------------------+
|         Streamlit UI          |
| (frontend/streamlit_app.py)   |
+---------------+---------------+
                |
                | HTTP (POST /api/v1/autocomplete)
                v
+-------------------------------+
|           FastAPI API         |
|  /api/routes/autocomplete     |
+---------------+---------------+
                |
                | DI (Depends)
                v
+-------------------------------+
|     AutocompleteService       |
|  - Singleton pattern          |
|  - LLM or Mock fallback       |
|  - Category assignment        |
+---------------+---------------+
                |
                | (Optional future: DB / Cache / Metrics)
                v
          External Services
        (Vertex AI / Law DB / etc.)
```

---

## 📁 Directory Structure

```
.
├── backend
│   └── app
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   └── logging_config.py
│       ├── api/
│       │   ├── routes/
│       │   │   ├── autocomplete.py
│       │   │   └── health.py
│       │   └── dependencies/
│       │       ├── auth.py
│       │       ├── logger.py
│       │       └── services.py
│       ├── services/
│       │   └── autocomplete_service.py
│       ├── models/
│       │   ├── enums/
│       │   │   └── language_code.py
│       │   └── schemas/
│       │       ├── autocomplete.py
│       │       └── common.py
│       └── prompts/
│           └── autocomplete.py
├── frontend
│   ├── streamlit_app.py
│   └── components/
│       ├── autocomplete_client.py
│       └── throttle.py
├── tests/
│   └── test_autocomplete_service.py
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Environment Variables

Create a `.env` from the example:

```
cp .env.example .env
```

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| APP_ENV | No | dev | Environment tag |
| LOG_LEVEL | No | INFO | Logging level |
| APP_NAME | No | Legal Autocomplete Service | Service display name |
| ENABLE_VERTEX | No | false | Enable Vertex AI (LLM) |
| VERTEX_PROJECT | If ENABLE_VERTEX=true | - | GCP Project ID |
| VERTEX_LOCATION | If ENABLE_VERTEX=true | us-central1 | Region |
| VERTEX_MODEL_NAME | If ENABLE_VERTEX=true | gemini-1.5-flash | LLM model name |

If `ENABLE_VERTEX=false`, a mock deterministic generator is used (no external calls).

---

## 🚀 Quick Start (Local)

### 1. Prerequisites
- Python 3.11+
- (Optional) Google Cloud project + Vertex AI (for real LLM)

### 2. Install Backend & Frontend
```
python -m venv .venv
source .venv/Scripts/activate  # (Windows: .venv\Scripts\activate)
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

### 3. Run Backend
```
uvicorn backend.app.main:app --reload
```
API Docs: http://localhost:8000/docs  
Health: http://localhost:8000/api/v1/health

### 4. Run Streamlit Frontend
```
streamlit run frontend/streamlit_app.py
```
Visit: http://localhost:8501

---

## 🐳 Docker

### Compose (Backend + Frontend)
```
docker-compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:8501

### Build Individually
```
docker build -f docker/backend.Dockerfile -t law-autocomplete-backend .
docker run -p 8000:8000 --env-file .env law-autocomplete-backend
```

---

## 🔌 API Usage

### Endpoint
`POST /api/v1/autocomplete`

### Request Body
```json
{
  "input": "contract termina",
  "max_predictions": 5,
  "categories": ["Contract Law", "Consumer Rights"],
  "output_language": "en"
}
```

### Successful Response
```json
{
  "success": true,
  "message": "Autocomplete suggestions generated successfully.",
  "data": {
    "suggestions": [
      { "text": "contract termination rights under BGB", "category": "Contract Law" },
      { "text": "contract termination notice period", "category": "Other (Misc.)" }
    ]
  }
}
```

### Curl Example
```bash
curl -X POST http://localhost:8000/api/v1/autocomplete \
  -H "Content-Type: application/json" \
  -d '{"input":"residence permit","max_predictions":5,"categories":["Immigration"],"output_language":"en"}'
```

---

## 🧠 LLM Integration (Vertex AI)

If you enable Vertex:
1. Enable API: `gcloud services enable aiplatform.googleapis.com`
2. Auth locally:
   ```
   gcloud auth application-default login
   ```
3. Set `.env`:
   ```
   ENABLE_VERTEX=true
   VERTEX_PROJECT=your-project-id
   VERTEX_LOCATION=us-central1
   VERTEX_MODEL_NAME=gemini-1.5-flash
   ```

If disabled, mock suggestions allow development without credentials.

---

## 🛡️ Security & Hardening (Recommended Future Steps)

| Concern | Recommendation |
|---------|----------------|
| Rate limiting | Add FastAPI middleware or a gateway (e.g., Traefik / Cloudflare) |
| Auth | Replace stub auth with JWT / OAuth2 / API Keys |
| Abuse filtering | Enhance `_spammy` heuristic & add entropy/hamming filters |
| Observability | Add OpenTelemetry tracing + Prometheus metrics |
| Caching | LRU or Redis to cut LLM latency for repeated prefixes |
| Streaming | Provide SSE/WebSocket for incremental suggestion updates |

---

## 🧪 Testing

```
pytest -q
```

Add more tests under `tests/`:
- Service logic
- Spam guard
- LLM fallback handling
- Performance regression (optional)

---

## 🚦 Development Workflow

| Task | Command |
|------|---------|
| Run backend | `uvicorn backend.app.main:app --reload` |
| Run frontend | `streamlit run frontend/streamlit_app.py` |
| Format (add your tool) | e.g. `ruff check .` |
| Tests | `pytest -q` |
| Type check | `mypy backend/` (if added) |

---

## 🔄 Real-Time Frontend Behavior

The Streamlit app:
- Calls the backend as you type (no Enter key)
- Debounces calls (default 250 ms)
- Highlights the completion suffix
- Clickable suggestions adopt text instantly

To tweak behavior:
- Adjust debounce in sidebar
- Lower min chars for earlier triggering
- Add caching (already implemented via `functools.lru_cache`)

---

## 🗺️ Roadmap (Suggested)

| Stage | Feature |
|-------|---------|
| 1 | Plug in real law category DB (Postgres / Mongo) |
| 1 | Add multi-tenant auth (JWT) |
| 2 | Redis caching layer |
| 2 | WebSocket live updates |
| 2 | Metrics dashboard (Grafana) |
| 3 | Adaptive ranking (track user clicks) |
| 3 | Add semantic filtering (embedding guard) |
| 4 | Package as pip library (`law-autocomplete-client`) |

---

## 🤝 Contributing

1. Fork repo
2. Create feature branch: `git checkout -b feat/my-feature`
3. Commit changes: `git commit -m "feat: add X"`
4. Push: `git push origin feat/my-feature`
5. Open Pull Request

Please:
- Include tests for new logic
- Use clear commit messages (Conventional Commits recommended)
- Avoid committing secrets / `.env`

---

## 📄 License

MIT License (add `LICENSE` file if not present).

---

## 💬 Support / Questions

Open an Issue or start a Discussion (if enabled).  
For advanced enhancements (e.g., turning into a SaaS module) feel free to propose an Architecture Issue.

---

## ✅ Quick Validation Checklist

| Item | Verified / Adjustable |
|------|------------------------|
| Real-time UI | Yes |
| LLM fallback | Yes |
| Config via `.env` | Yes |
| Dockerized | Yes |
| Test scaffold | Yes |
| Prompt isolation | Yes |
| Category normalization | Yes |
| Extensible service code | Yes |

---

## 🧾 Attribution / Inspiration

- FastAPI design patterns
- Google Vertex AI Gemini (optional)
- Streamlit rapid prototyping UX

---

If you’d like a version of this README branded under a new project name (e.g., “LexiComplete”), or want CI badges / GitHub Actions workflows added, just ask!

**Author:** Syed Afraz  
