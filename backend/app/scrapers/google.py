from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
import requests
from pydantic import BaseModel
from app.utils.markdown_converter import MarkdownConverter


class GoogleArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None


class GoogleScraper:
    def __init__(self):
        # Google AI blog RSS feed
        self.rss_url = "https://blog.google/technology/ai/rss/"
        self.converter = MarkdownConverter()

    def get_articles(self, hours: int = 24) -> List[GoogleArticle]:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(self.rss_url, headers=headers)
        feed = feedparser.parse(response.content)
        if not feed.entries:
            return []
        
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        articles = []
        
        for entry in feed.entries:
            published_parsed = getattr(entry, "published_parsed", None)
            if not published_parsed:
                continue
            
            published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
            if published_time >= cutoff_time:
                articles.append(GoogleArticle(
                    title=entry.get("title", ""),
                    description=entry.get("description", ""),
                    url=entry.get("link", ""),
                    guid=entry.get("id", entry.get("link", "")),
                    published_at=published_time,
                    category=entry.get("tags", [{}])[0].get("term") if entry.get("tags") else None
                ))
        
        return articles

    def url_to_markdown(self, url: str) -> Optional[str]:
        return self.converter.convert_url(url)


if __name__ == "__main__":
    scraper = GoogleScraper()
    articles: List[GoogleArticle] = scraper.get_articles(hours=50)
    print(f"Found {len(articles)} articles")
    if articles:
        print(f"First article: {articles[0].title}")
        print(f"Published: {articles[0].published_at}")
