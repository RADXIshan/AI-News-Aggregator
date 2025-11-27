from datetime import datetime, timedelta, timezone
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from app.utils.markdown_converter import MarkdownConverter


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
        self.converter = MarkdownConverter()

    def _fetch_paper_description(self, paper_url: str, headers: dict) -> str:
        """Fetch the abstract/description from an individual paper page"""
        try:
            response = requests.get(paper_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find the abstract section
            # Look for heading with "Abstract" text
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                if 'abstract' in heading.get_text().lower():
                    # Get the next paragraph after the abstract heading
                    next_elem = heading.find_next_sibling('p')
                    if next_elem:
                        description = next_elem.get_text(strip=True)
                        # Make sure it's not a generic message
                        if description and len(description) > 50 and 'join the discussion' not in description.lower():
                            return description
            
            # Try to find paragraphs with substantial content (likely abstract)
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Filter out generic messages and look for substantial content
                if (len(text) > 100 and 
                    'join the discussion' not in text.lower() and
                    'code and data' not in text.lower() and
                    'http' not in text.lower()):
                    return text
            
            return ""
        except Exception as e:
            print(f"Error fetching description for {paper_url}: {e}")
            return ""

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
                    
                    # Fetch description from individual paper page
                    description = self._fetch_paper_description(url, headers)
                    
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

    def url_to_markdown(self, url: str) -> Optional[str]:
        return self.converter.convert_url(url)


if __name__ == "__main__":
    scraper = HuggingFacePapersScraper()
    papers: List[HuggingFacePaper] = scraper.get_papers()
    print(f"Found {len(papers)} papers")
    if papers:
        print(f"First paper: {papers[0].title}")
        print(f"URL: {papers[0].url}")
