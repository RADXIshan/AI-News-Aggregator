from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.mistral import MistralScraper
from app.database.repository import Repository


def process_mistral_markdown(limit: Optional[int] = None) -> dict:
    scraper = MistralScraper()
    repo = Repository()
    
    try:
        articles = repo.get_mistral_articles_without_markdown(limit=limit)
        
        processed = 0
        failed = 0
        
        for article in articles:
            try:
                markdown = scraper.url_to_markdown(article.url)
                if markdown:
                    repo.update_mistral_article_markdown(article.guid, markdown)
                    processed += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"Error processing article {article.guid}: {e}")
                continue
        
        return {
            "total": len(articles),
            "processed": processed,
            "failed": failed
        }
    finally:
        repo.session.close()


if __name__ == "__main__":
    result = process_mistral_markdown()
    print(f"Total articles: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Failed: {result['failed']}")
