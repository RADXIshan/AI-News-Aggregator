from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
import requests
from pydantic import BaseModel
from app.utils.markdown_converter import MarkdownConverter


class AnthropicArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None


class AnthropicScraper:
    def __init__(self):
        self.rss_urls = [
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        ]
        self.converter = MarkdownConverter()

    def get_articles(self, hours: int = 24) -> List[AnthropicArticle]:
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        articles = []
        seen_guids = set()
        
        for rss_url in self.rss_urls:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(rss_url, headers=headers)
            feed = feedparser.parse(response.content)
            if not feed.entries:
                continue
            
            for entry in feed.entries:
                published_parsed = getattr(entry, "published_parsed", None)
                if not published_parsed:
                    continue
                
                published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                if published_time >= cutoff_time:
                    guid = entry.get("id", entry.get("link", ""))
                    if guid not in seen_guids:
                        seen_guids.add(guid)
                        articles.append(AnthropicArticle(
                            title=entry.get("title", ""),
                            description=entry.get("description", ""),
                            url=entry.get("link", ""),
                            guid=guid,
                            published_at=published_time,
                            category=entry.get("tags", [{}])[0].get("term") if entry.get("tags") else None
                        ))
        
        return articles

    def url_to_markdown(self, url: str) -> Optional[str]:
        return self.converter.convert_url(url)

if __name__ == "__main__":
    scraper = AnthropicScraper()
    articles: List[AnthropicArticle] = scraper.get_articles(hours=100)
    markdown: str = scraper.url_to_markdown(articles[1].url)
    print(markdown)