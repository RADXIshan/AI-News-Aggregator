import requests
from bs4 import BeautifulSoup
import html2text
from typing import Optional


class MarkdownConverter:
    def __init__(self):
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = False
        self.html2text.ignore_images = False
        self.html2text.body_width = 0  # Don't wrap text
        
    def convert_url(self, url: str, timeout: int = 10) -> Optional[str]:
        """Convert a URL to markdown format"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get the main content (try common article containers)
            main_content = (
                soup.find('article') or 
                soup.find('main') or 
                soup.find('div', class_='content') or
                soup.find('div', class_='post-content') or
                soup.body
            )
            
            if not main_content:
                return None
            
            # Convert to markdown
            html_content = str(main_content)
            markdown = self.html2text.handle(html_content)
            
            return markdown.strip()
            
        except Exception as e:
            print(f"Error converting URL {url}: {e}")
            return None
