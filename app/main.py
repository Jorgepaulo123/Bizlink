from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import auth as auth_router
from .routers import users as users_router
from .routers import companies as companies_router
from .routers import services as services_router
from .routers import files as files_router
from fastapi.staticfiles import StaticFiles
from .settings import settings

# Create/alter tables (simple dev mode). For production, use proper migrations.
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

app = FastAPI(title="BizLinkApi", version="0.1.0")

# CORS
# Read from settings.CORS_ORIGINS (comma-separated). If '*' is present, ignore it when credentials are enabled.
_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")] if getattr(settings, "CORS_ORIGINS", None) else []
_origins = [o for o in _origins if o and o != "*"]
if not _origins:
    # Fallback sensible defaults for dev
    _origins = ["http://localhost:5173", "http://localhost:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,  # Configured via settings.CORS_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Routers
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(users_router.router, prefix="/users", tags=["users"])
app.include_router(companies_router.router, prefix="/companies", tags=["companies"])
app.include_router(services_router.router, prefix="/services", tags=["services"])
app.include_router(files_router.router, prefix="/files", tags=["files"])

# Static uploads
import os as _os
_uploads_dir = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "uploads"))
_os.makedirs(_uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads_dir), name="uploads")

@app.get("/")
def read_root():
    return {"name": "BizLinkApi", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Use import string to support reload when running as script inside the app folder
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)