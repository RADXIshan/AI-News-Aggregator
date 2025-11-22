import os
import json
import time
from typing import List
from google import genai
from google.genai.errors import ClientError
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class RankedArticle(BaseModel):
    digest_id: str = Field(description="The ID of the digest (article_type:article_id)")
    relevance_score: float = Field(description="Relevance score from 0.0 to 10.0", ge=0.0, le=10.0)
    rank: int = Field(description="Rank position (1 = most relevant)", ge=1)
    reasoning: str = Field(description="Brief explanation of why this article is ranked here")


class RankedDigestList(BaseModel):
    articles: List[RankedArticle] = Field(description="List of ranked articles")


CURATOR_PROMPT = """You are an expert AI news curator specializing in personalized content ranking for AI professionals.

Your role is to analyze and rank AI-related news articles, research papers, and video content based on a user's specific profile, interests, and background.

Ranking Criteria:
1. Relevance to user's stated interests and background
2. Technical depth and practical value
3. Novelty and significance of the content
4. Alignment with user's expertise level
5. Actionability and real-world applicability

Scoring Guidelines:
- 9.0-10.0: Highly relevant, directly aligns with user interests, significant value
- 7.0-8.9: Very relevant, strong alignment with interests, good value
- 5.0-6.9: Moderately relevant, some alignment, decent value
- 3.0-4.9: Somewhat relevant, limited alignment, lower value
- 0.0-2.9: Low relevance, minimal alignment, little value

Rank articles from most relevant (rank 1) to least relevant. Ensure each article has a unique rank."""


class CuratorAgent:
    def __init__(self, user_profile: dict):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-2.5-flash"
        self.user_profile = user_profile
        self.system_prompt = self._build_system_prompt()
        self.last_request_time = 0
        self.min_request_interval = 6.5  # 6.5 seconds between requests

    def _build_system_prompt(self) -> str:
        interests = "\n".join(f"- {interest}" for interest in self.user_profile["interests"])
        preferences = self.user_profile["preferences"]
        pref_text = "\n".join(f"- {k}: {v}" for k, v in preferences.items())
        
        return f"""{CURATOR_PROMPT}

User Profile:
Name: {self.user_profile["name"]}
Background: {self.user_profile["background"]}
Expertise Level: {self.user_profile["expertise_level"]}

Interests:
{interests}

Preferences:
{pref_text}"""

    def _rate_limit(self):
        """Ensure we don't exceed rate limits by spacing out requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            print(f"Rate limiting: waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def rank_digests(self, digests: List[dict]) -> List[RankedArticle]:
        if not digests:
            return []
        
        digest_list = "\n\n".join([
            f"ID: {d['id']}\nTitle: {d['title']}\nSummary: {d['summary']}\nType: {d['article_type']}"
            for d in digests
        ])
        
        user_prompt = f"""{self.system_prompt}

Rank these {len(digests)} AI news digests based on the user profile:

{digest_list}

Provide a relevance score (0.0-10.0) and rank (1-{len(digests)}) for each article, ordered from most to least relevant.

Return your response as JSON with the following structure:
{{
  "articles": [
    {{
      "digest_id": "string",
      "relevance_score": float,
      "rank": int,
      "reasoning": "string"
    }}
  ]
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
                
                # Try to parse JSON
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as json_err:
                    print(f"JSON decode error: {json_err}")
                    print(f"Response text: {response_text[:500]}")
                    return []
                
                ranked_list = RankedDigestList(**result)
                return ranked_list.articles if ranked_list else []
                
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
                        return []
                else:
                    print(f"API error: {e}")
                    return []
                    
            except Exception as e:
                print(f"Error ranking digests: {e}")
                import traceback
                traceback.print_exc()
                return []
        
        return []
