from datetime import datetime, timedelta, timezone
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from app.utils.markdown_converter import MarkdownConverter


class MistralArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None


class MistralScraper:
    def __init__(self):
        self.news_url = "https://mistral.ai/news/"
        self.converter = MarkdownConverter()

    def get_articles(self, hours: int = 24) -> List[MistralArticle]:
        """Scrape Mistral AI news directly from the webpage"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            response = requests.get(self.news_url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            now = datetime.now(timezone.utc)
            cutoff_time = now - timedelta(hours=hours)
            
            # Find article elements - Mistral uses various selectors
            article_elements = (
                soup.find_all('article') or
                soup.find_all('div', class_=lambda x: x and ('news' in x.lower() or 'post' in x.lower() or 'card' in x.lower())) or
                soup.find_all('a', href=lambda x: x and '/news/' in x and x != '/news/')
            )
            
            seen_urls = set()
            
            for element in article_elements[:20]:  # Limit to 20 most recent
                try:
                    # Find link
                    if element.name == 'a':
                        link = element
                    else:
                        link = element.find('a', href=True)
                    
                    if not link or not link.get('href'):
                        continue
                    
                    url = link['href']
                    if not url.startswith('http'):
                        url = 'https://mistral.ai' + url
                    
                    # Skip if already seen or not a news post
                    if url in seen_urls or '/news/' not in url or url == 'https://mistral.ai/news/':
                        continue
                    
                    seen_urls.add(url)
                    
                    # Find title
                    title_elem = (
                        element.find('h1') or 
                        element.find('h2') or 
                        element.find('h3') or
                        element.find('h4') or
                        link
                    )
                    title = title_elem.get_text(strip=True) if title_elem else "Untitled"
                    
                    # Find description
                    desc_elem = element.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Find date
                    date_elem = element.find('time')
                    if date_elem and date_elem.get('datetime'):
                        try:
                            published_at = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
                        except:
                            published_at = now
                    else:
                        # Use current time for articles without dates
                        published_at = now
                    
                    # Only include if within time range
                    if published_at >= cutoff_time:
                        articles.append(MistralArticle(
                            title=title,
                            description=description[:500] if description else "",
                            url=url,
                            guid=url,
                            published_at=published_at,
                            category="News"
                        ))
                
                except Exception as e:
                    continue
            
            return articles
            
        except Exception as e:
            print(f"Error scraping Mistral AI news: {e}")
            return []

    def url_to_markdown(self, url: str) -> Optional[str]:
        return self.converter.convert_url(url)


if __name__ == "__main__":
    scraper = MistralScraper()
    articles: List[MistralArticle] = scraper.get_articles(hours=100)
    print(f"Found {len(articles)} articles")
    if articles:
        print(f"First article: {articles[0].title}")
        print(f"Published: {articles[0].published_at}")
