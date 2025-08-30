from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .settings import settings

class Base(DeclarativeBase):
    pass

# Lazy engine creation
_engine = None
_SessionLocal = None

def get_engine():
    """Get database engine, creating it if necessary"""
    global _engine
    if _engine is None:
        try:
            DATABASE_URL = settings.DATABASE_URL
            # Force use of psycopg2 dialect
            if DATABASE_URL.startswith('postgresql://'):
                DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://')
            
            _engine = create_engine(DATABASE_URL)
            print("✅ Database engine created successfully")
        except Exception as e:
            print(f"⚠️ Failed to create database engine: {e}")
            # Create a dummy engine that will fail gracefully
            _engine = create_engine("sqlite:///:memory:")
    
    return _engine

def get_session_local():
    """Get session local, creating it if necessary"""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return _SessionLocal

# Dependency
def get_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
