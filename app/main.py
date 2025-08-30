from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .database import Base, engine
from .routers import auth as auth_router
from .routers import users as users_router
from .routers import companies as companies_router
from .routers import services as services_router
from .routers import credits as credits_router
from .routers import profile as profile_router
from .routers import files as files_router
from .routers import search as search_router
from fastapi.staticfiles import StaticFiles
from .settings import settings

# Create/alter tables (simple dev mode). For production, use proper migrations.
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

app = FastAPI(title="BizLinkApi", version="0.1.0")

# CORS wildcard with credentials (as requested)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bizlink-mz.vercel.app", "https://lovable.dev"],  # domínio do teu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(users_router.router, prefix="/users", tags=["users"])
app.include_router(companies_router.router, prefix="/companies", tags=["companies"])
app.include_router(services_router.router, prefix="/services", tags=["services"])
app.include_router(credits_router.router, prefix="/credits", tags=["credits"])
app.include_router(profile_router.router, prefix="/profile", tags=["profile"])
app.include_router(files_router.router, prefix="/files", tags=["files"])
app.include_router(search_router.router, prefix="/search", tags=["search"])

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
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)