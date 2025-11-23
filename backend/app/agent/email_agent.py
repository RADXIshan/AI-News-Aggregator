import os
import json
import time
from datetime import datetime, timezone
from typing import List, Optional
from google import genai
from google.genai.errors import ClientError
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from app.config import USER_TIMEZONE

load_dotenv()


class EmailIntroduction(BaseModel):
    greeting: str = Field(description="Personalized greeting with user's name and date")
    introduction: str = Field(description="2-3 sentence overview of what's in the top 10 ranked articles")

class RankedArticleDetail(BaseModel):
    digest_id: str
    rank: int
    relevance_score: float
    title: str
    summary: str
    url: str
    article_type: str
    reasoning: Optional[str] = None


class EmailDigestResponse(BaseModel):
    introduction: EmailIntroduction
    articles: List[RankedArticleDetail]
    total_ranked: int
    top_n: int
    
    def to_markdown(self) -> str:
        markdown = f"{self.introduction.greeting}\n\n"
        markdown += f"{self.introduction.introduction}\n\n"
        markdown += "---\n\n"
        
        for article in self.articles:
            markdown += f"## {article.title}\n\n"
            markdown += f"{article.summary}\n\n"
            markdown += f"[Read more →]({article.url})\n\n"
            markdown += "---\n\n"
        
        return markdown


class EmailDigest(BaseModel):
    introduction: EmailIntroduction
    ranked_articles: List[dict] = Field(description="Top 10 ranked articles with their details")


EMAIL_PROMPT = """You are an expert email writer specializing in creating engaging, personalized AI news digests.

Your role is to write a warm, professional introduction for a daily AI news digest email that:
- Greets the user by name
- Includes the current date
- Provides a brief, engaging overview of what's coming in the top 10 ranked articles
- Highlights the most interesting or important themes
- Sets expectations for the content ahead

Keep it concise (2-3 sentences for the introduction), friendly, and professional."""


class EmailAgent:
    def __init__(self, user_profile: dict):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-2.5-flash-lite"
        self.user_profile = user_profile
        self.last_request_time = 0
        self.min_request_interval = 6.5  # 6.5 seconds between requests

    def _rate_limit(self):
        """Ensure we don't exceed rate limits by spacing out requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            print(f"Rate limiting: waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def generate_introduction(self, ranked_articles: List) -> EmailIntroduction:
        if not ranked_articles:
            current_date = datetime.now(timezone.utc).astimezone(USER_TIMEZONE).strftime('%B %d, %Y')
            return EmailIntroduction(
                greeting=f"Hey {self.user_profile['name']}, here is your daily digest of AI news for {current_date}.",
                introduction="No articles were ranked today."
            )
        
        top_articles = ranked_articles[:10]
        article_summaries = "\n".join([
            f"{idx + 1}. {article.title if hasattr(article, 'title') else article.get('title', 'N/A')} (Score: {article.relevance_score if hasattr(article, 'relevance_score') else article.get('relevance_score', 0):.1f}/10)"
            for idx, article in enumerate(top_articles)
        ])
        
        current_date = datetime.now(timezone.utc).astimezone(USER_TIMEZONE).strftime('%B %d, %Y')
        user_prompt = f"""{EMAIL_PROMPT}

Create an email introduction for {self.user_profile['name']} for {current_date}.

Top 10 ranked articles:
{article_summaries}

Generate a greeting and introduction that previews these articles.

Return your response as JSON with the following structure:
{{
  "greeting": "string",
  "introduction": "string"
}}"""

        max_retries = 3
        base_delay = 10
        
        for attempt in range(max_retries):
            try:
                # Rate limit before making request
                self._rate_limit()
                
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
                
                intro = EmailIntroduction(**result)
                current_date_check = datetime.now(timezone.utc).astimezone(USER_TIMEZONE).strftime('%B %d, %Y')
                if not intro.greeting.startswith(f"Hey {self.user_profile['name']}"):
                    intro.greeting = f"Hey {self.user_profile['name']}, here is your daily digest of AI news for {current_date_check}."
                
                return intro
                
            except ClientError as e:
                if e.status_code == 429:  # Rate limit error
                    if attempt < max_retries - 1:
                        retry_delay = base_delay * (2 ** attempt)
                        try:
                            import re
                            match = re.search(r'(\d+\.?\d*)s', str(e))
                            if match:
                                retry_delay = float(match.group(1)) + 1
                        except:
                            pass
                        
                        print(f"Rate limit hit. Retrying in {retry_delay:.1f}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"Rate limit exceeded after {max_retries} attempts: {e}")
                        break
                else:
                    print(f"API error: {e}")
                    break
                    
            except Exception as e:
                print(f"Error generating introduction: {e}")
                import traceback
                traceback.print_exc()
                break
        
        # Fallback
        current_date = datetime.now(timezone.utc).astimezone(USER_TIMEZONE).strftime('%B %d, %Y')
        return EmailIntroduction(
            greeting=f"Hey {self.user_profile['name']}, here is your daily digest of AI news for {current_date}.",
            introduction="Here are the top 10 AI news articles ranked by relevance to your interests."
        )

    def create_email_digest(self, ranked_articles: List[dict], limit: int = 10) -> EmailDigest:
        top_articles = ranked_articles[:limit]
        introduction = self.generate_introduction(top_articles)
        
        return EmailDigest(
            introduction=introduction,
            ranked_articles=top_articles
        )
    
    def create_email_digest_response(self, ranked_articles: List[RankedArticleDetail], total_ranked: int, limit: int = 10) -> EmailDigestResponse:
        top_articles = ranked_articles[:limit]
        introduction = self.generate_introduction(top_articles)
        
        return EmailDigestResponse(
            introduction=introduction,
            articles=top_articles,
            total_ranked=total_ranked,
            top_n=limit
        )

