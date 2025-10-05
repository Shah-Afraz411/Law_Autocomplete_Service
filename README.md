# Law Autocomplete Service

This repository contains a simple scaffold for a law-focused autocomplete service with:

- FastAPI backend
- Streamlit frontend
- Minimal Dockerfiles and docker-compose
- A simple unit test for the autocomplete service

Quick start (local, no Docker):

1. Create and activate a virtualenv and install requirements:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the backend:

```powershell
uvicorn backend.app.main:app --reload
```

3. Run the frontend (in another shell):

```powershell
streamlit run frontend/streamlit_app.py
```

Run tests:

```powershell
pytest -q
```

