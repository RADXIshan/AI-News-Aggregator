import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def get_database_url() -> str:
    """
    Get database URL from environment.
    Prioritizes DATABASE_URL (for Neon and other cloud providers),
    falls back to individual PostgreSQL connection parameters.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Fallback to individual parameters
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ai_news_aggregator")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def get_database_info() -> dict:
    """
    Get database connection information for display/debugging
    """
    database_url = get_database_url()
    parsed = urlparse(database_url)
    
    # Mask password in URL
    if parsed.password:
        masked_url = database_url.replace(parsed.password, "****")
    else:
        masked_url = database_url
    
    # Determine environment
    if "neon" in parsed.hostname or "neon" in database_url:
        environment = "Neon (Cloud)"
    elif parsed.hostname in ["localhost", "127.0.0.1"]:
        environment = "Local"
    else:
        environment = "Remote"
    
    return {
        "url": database_url,
        "url_masked": masked_url,
        "host": parsed.hostname or "unknown",
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/") if parsed.path else "unknown",
        "environment": environment
    }


engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=300,    # Recycle connections after 5 minutes
    pool_size=1,         # Serverless: use minimal pool size
    max_overflow=0,      # Serverless: no overflow connections
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()

