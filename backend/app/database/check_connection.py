import sys
from app.database.connection import get_database_info, engine
from sqlalchemy import text

if __name__ == "__main__":
    db_info = get_database_info()

    print("\n" + "=" * 60)
    print("Database Connection Check")
    print("=" * 60)
    print(f"Environment: {db_info['environment']}")
    print(f"Database URL: {db_info['url_masked']}")
    print(f"Host: {db_info['host']}")
    print(f"Database: {db_info['database']}")
    print("=" * 60 + "\n")

    try:
        with engine.connect() as conn:
            # Check PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print("✓ Connection successful!")
            print(f"✓ PostgreSQL version: {version.split(',')[0]}")
            
            # Check tables exist
            tables = ['youtube_videos', 'openai_articles', 'anthropic_articles', 
                     'google_articles', 'digests', 'emails']
            
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"✓ Table '{table}' exists with {count} records")
                except Exception as e:
                    print(f"⚠ Table '{table}' not found or error: {e}")
            
            print("\n✓ Database connection and schema check complete!")

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)