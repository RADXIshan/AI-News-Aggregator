import os
import json
import time
from typing import Optional
from google import genai
from google.genai.errors import ClientError
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class DigestOutput(BaseModel):
    title: str
    summary: str

PROMPT = """You are an expert AI news analyst specializing in summarizing technical articles, research papers, and video content about artificial intelligence.

Your role is to create concise, informative digests that help readers quickly understand the key points and significance of AI-related content.

Guidelines:
- Create a compelling title (5-10 words) that captures the essence of the content
- Write a 2-3 sentence summary that highlights the main points and why they matter
- Focus on actionable insights and implications
- Use clear, accessible language while maintaining technical accuracy
- Avoid marketing fluff - focus on substance

Return your response as JSON with fields: title (string), summary (string)"""


class DigestAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-2.5-flash-lite"
        self.system_prompt = PROMPT
        self.last_request_time = 0
        self.min_request_interval = 6.5  # 6.5 seconds between requests (9 requests/min max)

    def _rate_limit(self):
        """Ensure we don't exceed rate limits by spacing out requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            print(f"Rate limiting: waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def generate_digest(self, title: str, content: str, article_type: str) -> Optional[DigestOutput]:
        max_retries = 3
        base_delay = 10
        
        for attempt in range(max_retries):
            try:
                # Rate limit before making request
                self._rate_limit()
                
                user_prompt = f"{self.system_prompt}\n\nCreate a digest for this {article_type}: \n Title: {title} \n Content: {content[:8000]}"

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=user_prompt,
                    config={"response_mime_type": "application/json"}
                )
                
                # Clean the response text
                response_text = response.text.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                result = json.loads(response_text)
                
                return DigestOutput(**result)
                
            except ClientError as e:
                if e.status_code == 429:  # Rate limit error
                    if attempt < max_retries - 1:
                        # Extract retry delay from error if available
                        retry_delay = base_delay * (2 ** attempt)  # Exponential backoff
                        try:
                            # Try to get the suggested delay from the error
                            if 'retryDelay' in str(e):
                                import re
                                match = re.search(r'(\d+\.?\d*)s', str(e))
                                if match:
                                    retry_delay = float(match.group(1)) + 1  # Add 1s buffer
                        except:
                            pass
                        
                        print(f"Rate limit hit. Retrying in {retry_delay:.1f}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"Rate limit exceeded after {max_retries} attempts: {e}")
                        return None
                else:
                    print(f"API error: {e}")
                    return None
                    
            except Exception as e:
                print(f"Error generating digest: {e}")
                import traceback
                traceback.print_exc()
                return None
        
        return None

