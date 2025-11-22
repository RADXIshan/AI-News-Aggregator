from datetime import datetime, timedelta, timezone
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


class HuggingFacePaper(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    upvotes: Optional[int] = None


class HuggingFacePapersScraper:
    def __init__(self):
        self.base_url = "https://huggingface.co/papers"

    def get_papers(self, hours: int = 24) -> List[HuggingFacePaper]:
        """Scrape trending papers from Hugging Face Papers"""
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            response = requests.get(self.base_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            papers = []
            now = datetime.now(timezone.utc)
            
            # Find paper cards - adjust selectors based on actual HTML structure
            paper_elements = soup.find_all('article', limit=20)  # Get top 20 trending papers
            
            for idx, element in enumerate(paper_elements):
                try:
                    # Extract title
                    title_elem = element.find('h3') or element.find('h4')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract URL
                    link_elem = element.find('a', href=True)
                    if not link_elem:
                        continue
                    url = link_elem['href']
                    if not url.startswith('http'):
                        url = f"https://huggingface.co{url}"
                    
                    # Extract description/abstract
                    desc_elem = element.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Use URL as guid
                    guid = url
                    
                    # For trending papers, use current time as published_at
                    # since we don't have exact publication time
                    published_at = now
                    
                    papers.append(HuggingFacePaper(
                        title=title,
                        description=description,
                        url=url,
                        guid=guid,
                        published_at=published_at,
                        upvotes=None
                    ))
                except Exception as e:
                    continue
            
            return papers
            
        except Exception as e:
            print(f"Error scraping Hugging Face papers: {e}")
            return []


if __name__ == "__main__":
    scraper = HuggingFacePapersScraper()
    papers: List[HuggingFacePaper] = scraper.get_papers()
    print(f"Found {len(papers)} papers")
    if papers:
        print(f"First paper: {papers[0].title}")
        print(f"URL: {papers[0].url}")
