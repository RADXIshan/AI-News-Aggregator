from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.huggingface_papers import HuggingFacePapersScraper
from app.database.repository import Repository


def process_huggingface_papers_markdown(limit: Optional[int] = None) -> dict:
    scraper = HuggingFacePapersScraper()
    repo = Repository()
    
    try:
        papers = repo.get_huggingface_papers_without_markdown(limit=limit)
        
        processed = 0
        failed = 0
        
        for paper in papers:
            try:
                markdown = scraper.url_to_markdown(paper.url)
                if markdown:
                    repo.update_huggingface_paper_markdown(paper.guid, markdown)
                    processed += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"Error processing paper {paper.guid}: {e}")
                continue
        
        return {
            "total": len(papers),
            "processed": processed,
            "failed": failed
        }
    finally:
        repo.session.close()


if __name__ == "__main__":
    result = process_huggingface_papers_markdown()
    print(f"Total papers: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Failed: {result['failed']}")
