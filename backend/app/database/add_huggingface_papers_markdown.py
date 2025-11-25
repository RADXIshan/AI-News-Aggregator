"""
Migration script to add markdown column to huggingface_papers table
"""
import sys
import logging
from sqlalchemy import text
from app.database.connection import engine, get_database_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_markdown_column():
    """Add markdown column to huggingface_papers table if it doesn't exist"""
    try:
        db_info = get_database_info()
        
        logger.info("=" * 60)
        logger.info("Database Migration: Add markdown to huggingface_papers")
        logger.info("=" * 60)
        logger.info(f"Environment: {db_info['environment']}")
        logger.info(f"Database: {db_info['database']}")
        logger.info("=" * 60)
        
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='huggingface_papers' 
                AND column_name='markdown'
            """))
            
            if result.fetchone():
                logger.info("✓ Column 'markdown' already exists in huggingface_papers table")
                return True
            
            # Add the column
            logger.info("Adding 'markdown' column to huggingface_papers table...")
            conn.execute(text("""
                ALTER TABLE huggingface_papers 
                ADD COLUMN markdown TEXT
            """))
            conn.commit()
            
            logger.info("✓ Successfully added 'markdown' column to huggingface_papers table")
            return True
        
    except Exception as e:
        logger.error(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = add_markdown_column()
    sys.exit(0 if success else 1)
