from typing import Optional
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agent.digest_agent import DigestAgent
from app.database.repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def process_digests(limit: Optional[int] = None) -> dict:
    agent = DigestAgent()
    
    # Use a single repository instance with proper session management
    repo = Repository()
    try:
        articles = repo.get_articles_without_digest(limit=limit)
        
        total = len(articles)
        processed = 0
        failed = 0
        
        logger.info(f"Starting digest processing for {total} articles")
        
        for idx, article in enumerate(articles, 1):
            article_type = article["type"]
            article_id = article["id"]
            article_title = article["title"][:60] + "..." if len(article["title"]) > 60 else article["title"]
            
            logger.info(f"[{idx}/{total}] Processing {article_type}: {article_title} (ID: {article_id})")
            
            # Check if article has content
            content = article.get("content", "")
            if not content or not content.strip():
                failed += 1
                logger.warning(f"✗ Article has no content for {article_type} {article_id}")
                continue
            
            try:
                digest_result = agent.generate_digest(
                    title=article["title"],
                    content=content,
                    article_type=article_type
                )
                
                if digest_result:
                    # Validate digest has content before creating
                    if not digest_result.title or not digest_result.title.strip():
                        failed += 1
                        logger.warning(f"✗ Digest has empty title for {article_type} {article_id}")
                    elif not digest_result.summary or not digest_result.summary.strip():
                        failed += 1
                        logger.warning(f"✗ Digest has empty summary for {article_type} {article_id}")
                    else:
                        created_digest = repo.create_digest(
                            article_type=article_type,
                            article_id=article_id,
                            url=article["url"],
                            title=digest_result.title,
                            summary=digest_result.summary,
                            published_at=article.get("published_at")
                        )
                        if created_digest:
                            processed += 1
                            logger.info(f"✓ Successfully created digest for {article_type} {article_id}")
                        else:
                            failed += 1
                            logger.warning(f"✗ Failed to save digest for {article_type} {article_id}")
                else:
                    failed += 1
                    logger.warning(f"✗ Failed to generate digest for {article_type} {article_id}")
            except Exception as e:
                failed += 1
                logger.error(f"✗ Error processing {article_type} {article_id}: {e}")
        
        logger.info(f"Processing complete: {processed} processed, {failed} failed out of {total} total")
        
        return {
            "total": total,
            "processed": processed,
            "failed": failed
        }
    finally:
        repo.session.close()  # Always close the session


if __name__ == "__main__":
    result = process_digests()
    print(f"Total articles: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Failed: {result['failed']}")

