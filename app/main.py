from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import auth as auth_router
from .routers import users as users_router
from .routers import companies as companies_router
from .routers import services as services_router
from .settings import settings

# Create tables (for simple demo; for production, use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="BizLinkApi", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(users_router.router, prefix="/users", tags=["users"])
app.include_router(companies_router.router, prefix="/companies", tags=["companies"])
app.include_router(services_router.router, prefix="/services", tags=["services"])

@app.get("/")
def read_root():
    return {"name": "BizLinkApi", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Use import string to support reload when running as script inside the app folder
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)