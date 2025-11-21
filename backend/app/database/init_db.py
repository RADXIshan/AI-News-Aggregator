"""
Initialize database tables
Run this script to create all necessary tables in your database
"""
import sys
from app.database.connection import engine, get_database_info
from app.database.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Create all tables defined in models"""
    try:
        db_info = get_database_info()
        
        logger.info("=" * 60)
        logger.info("Database Initialization")
        logger.info("=" * 60)
        logger.info(f"Environment: {db_info['environment']}")
        logger.info(f"Database URL: {db_info['url_masked']}")
        logger.info(f"Host: {db_info['host']}")
        logger.info(f"Database: {db_info['database']}")
        logger.info("=" * 60)
        
        logger.info("\nCreating tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("✓ All tables created successfully!")
        logger.info("\nTables created:")
        logger.info("  - youtube_videos")
        logger.info("  - openai_articles")
        logger.info("  - anthropic_articles")
        logger.info("  - google_articles")
        logger.info("  - digests")
        logger.info("  - emails")
        logger.info("\n✓ Database initialization complete!")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
