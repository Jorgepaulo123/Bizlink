# BizLinkApi

FastAPI backend for BizLink. Provides JWT auth, users, companies, and services endpoints.

## Features
- FastAPI + Pydantic
- SQLAlchemy ORM (SQLite by default)
- JWT auth (login/register)
- Users, Companies, Services CRUD
- CORS enabled for Vite (http://localhost:5173)

## Quickstart

1) Create and activate a virtual environment

```
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
```

2) Install dependencies

```
pip install -r BizLinkApi/requirements.txt
```

3) Run the API

```
uvicorn app.main:app --reload --port 8000 --app-dir BizLinkApi
```

API docs: http://localhost:8000/docs

## Environment
Create `.env` (or copy from `.env.example`).

```
SECRET_KEY=change_me
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
DATABASE_URL=sqlite:///./bizlink.db
CORS_ORIGINS=http://localhost:5173
```
