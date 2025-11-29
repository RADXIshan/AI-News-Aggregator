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


CURATOR_PROMPT = """You are an expert AI news curator with deep expertise in machine learning, AI research, and production systems.

Your role is to analyze and rank AI-related content with precision, considering multiple dimensions of relevance and value.

RANKING METHODOLOGY:

1. INTEREST ALIGNMENT (40% weight)
   - Direct match with user's stated interests (highest priority)
   - Related topics that complement their interests
   - Emerging areas adjacent to their focus
   - Consider both breadth and depth of coverage

2. TECHNICAL DEPTH & QUALITY (25% weight)
   - Substance over hype: prioritize technical details, benchmarks, code
   - Research rigor: novel methods, ablation studies, reproducibility
   - Production readiness: scalability, deployment considerations
   - Avoid marketing fluff, vague claims, or superficial coverage

3. PRACTICAL VALUE (20% weight)
   - Actionable insights: can the reader apply this?
   - Real-world impact: production case studies, benchmarks
   - Implementation details: code, architecture, best practices
   - Tools and frameworks that solve real problems

4. NOVELTY & SIGNIFICANCE (10% weight)
   - Breakthrough research or paradigm shifts
   - Major product launches or capabilities
   - Important industry trends or shifts
   - Avoid rehashing old news or obvious content

5. EXPERTISE ALIGNMENT (5% weight)
   - Match content complexity to user's expertise level
   - Advanced users: prefer research papers, deep dives, system design
   - Avoid oversimplified content for advanced users
   - Prefer content that challenges and educates

SOURCE PRIORITY BONUS:
   - TIER 1 (Primary AI Labs): Google, Anthropic, OpenAI, Meta - Add +0.5 to +1.5 bonus to base score
   - These are leading AI research organizations with direct impact on the field
   - Prioritize their announcements, research, and product launches
   - TIER 2 (Other Sources): Apply standard scoring without bonus

SCORING GUIDELINES:
- 9.5-10.0: Must-read. Directly addresses core interests with high technical value and practical impact
- 8.5-9.4: Excellent. Strong alignment with interests, significant technical depth or practical value
- 7.5-8.4: Very good. Clear relevance to interests with good technical content or actionable insights
- 6.5-7.4: Good. Relevant to interests with decent technical depth or practical value
- 5.5-6.4: Moderate. Some relevance but limited depth, novelty, or practical value
- 4.0-5.4: Fair. Tangentially relevant or lacks technical substance
- 2.0-3.9: Low. Minimal relevance, marketing-heavy, or superficial
- 0.0-1.9: Very low. Off-topic, pure marketing, or no value

CRITICAL RULES:
- Be discriminating: use the full 0-10 scale, not just 7-10
- Penalize marketing hype, vague claims, and superficial content
- Reward technical depth, benchmarks, code, and real-world results
- Consider recency: breaking news and fresh research rank higher
- Apply SOURCE PRIORITY BONUS: Google, Anthropic, OpenAI, Meta articles get +0.5 to +1.5 bonus
- Ensure each article has a unique rank (no ties)
- Provide specific, technical reasoning for each ranking"""


class CuratorAgent:
    def __init__(self, user_profile: dict):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-2.5-flash-lite"
        self.user_profile = user_profile
        self.system_prompt = self._build_system_prompt()
        self.last_request_time = 0
        self.min_request_interval = 6.5  # 6.5 seconds between requests

    def _build_system_prompt(self) -> str:
        # Group interests by category for better context
        interests = self.user_profile["interests"]
        interests_text = "\n".join(f"  {i+1}. {interest}" for i, interest in enumerate(interests))
        
        preferences = self.user_profile["preferences"]
        pref_list = []
        if preferences.get("prefer_practical"):
            pref_list.append("✓ Prioritize practical, actionable content")
        if preferences.get("prefer_technical_depth"):
            pref_list.append("✓ Prioritize technical depth and rigor")
        if preferences.get("prefer_research_breakthroughs"):
            pref_list.append("✓ Prioritize novel research and breakthroughs")
        if preferences.get("prefer_production_focus"):
            pref_list.append("✓ Prioritize production systems and real-world deployments")
        if preferences.get("avoid_marketing_hype"):
            pref_list.append("✗ Penalize marketing hype and superficial content")
        
        pref_text = "\n".join(pref_list)
        
        return f"""{CURATOR_PROMPT}

═══════════════════════════════════════════════════════════════
USER PROFILE
═══════════════════════════════════════════════════════════════

Name: {self.user_profile["name"]}
Title: {self.user_profile.get("title", "AI Professional")}
Background: {self.user_profile["background"]}
Expertise Level: {self.user_profile["expertise_level"]}

CORE INTERESTS (ranked by importance):
{interests_text}

CONTENT PREFERENCES:
{pref_text}

═══════════════════════════════════════════════════════════════"""

    def _rate_limit(self):
        """Ensure we don't exceed rate limits by spacing out requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            print(f"Rate limiting: waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _get_source_priority_bonus(self, article_type: str) -> float:
        """
        Calculate source priority bonus for tier 1 AI labs
        Returns bonus score to add to base relevance score
        """
        # Tier 1: Primary AI Labs (Google, Anthropic, OpenAI, Meta)
        tier1_sources = ['google', 'anthropic', 'openai', 'meta']
        
        article_type_lower = article_type.lower()
        
        # Check if article is from a tier 1 source
        for source in tier1_sources:
            if source in article_type_lower:
                return 1.0  # Add 1.0 bonus to tier 1 sources
        
        # Tier 2: All other sources get no bonus
        return 0.0

    def rank_digests(self, digests: List[dict]) -> List[RankedArticle]:
        if not digests:
            return []
        
        # Format digests with better structure
        digest_list = "\n\n".join([
            f"[{i+1}] ID: {d['id']}\n"
            f"    Type: {d['article_type']}\n"
            f"    Title: {d['title']}\n"
            f"    Summary: {d['summary']}"
            for i, d in enumerate(digests)
        ])
        
        user_prompt = f"""{self.system_prompt}

TASK: Rank these {len(digests)} AI news articles

ARTICLES TO RANK:
{digest_list}

INSTRUCTIONS:
1. Analyze each article against the user profile using the 5 ranking criteria
2. Assign a relevance score (0.0-10.0) using the full scale
3. Give preference to articles from Google, Anthropic, OpenAI, and Meta (tier 1 AI labs)
4. Rank from 1 (most relevant) to {len(digests)} (least relevant)
5. Provide specific, technical reasoning for each score
6. Be critical: penalize hype, reward substance

IMPORTANT:
- Use the FULL 0-10 scale (don't cluster scores in 7-10 range)
- Each article must have a UNIQUE rank (no ties)
- Reasoning should reference specific interests and criteria
- Consider: interest alignment, technical depth, practical value, novelty, expertise fit, SOURCE PRIORITY
- Articles from Google, Anthropic, OpenAI, Meta should rank higher when quality is comparable
- Keep reasoning concise (1-2 sentences) and avoid line breaks or special characters

Return your response as valid JSON (no line breaks in strings):
{{
  "articles": [
    {{
      "digest_id": "article_type:article_id",
      "relevance_score": 8.5,
      "rank": 1,
      "reasoning": "Specific technical reason referencing user interests"
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
                    print(f"Response text: {response_text[:1000]}")
                    
                    # Try to fix common JSON issues
                    # Replace control characters with spaces
                    import re
                    cleaned_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', response_text)
                    
                    try:
                        result = json.loads(cleaned_text)
                        print("✓ Successfully parsed after cleaning control characters")
                    except json.JSONDecodeError as second_err:
                        print(f"Still failed after cleaning: {second_err}")
                        print(f"Cleaned text sample: {cleaned_text[:1000]}")
                        return []
                
                ranked_list = RankedDigestList(**result)
                articles = ranked_list.articles if ranked_list else []
                
                # Post-process: apply source priority bonus and ensure proper ranking
                if articles:
                    # Apply source priority bonus to tier 1 sources
                    for article in articles:
                        # Extract article type from digest_id (format: "article_type:article_id")
                        article_type = article.digest_id.split(':')[0] if ':' in article.digest_id else ''
                        bonus = self._get_source_priority_bonus(article_type)
                        
                        if bonus > 0:
                            original_score = article.relevance_score
                            article.relevance_score = min(10.0, article.relevance_score + bonus)
                            print(f"✓ Applied +{bonus} bonus to {article_type}: {original_score:.1f} → {article.relevance_score:.1f}")
                    
                    # Sort by relevance score (descending) after applying bonuses
                    articles = sorted(articles, key=lambda x: x.relevance_score, reverse=True)
                    
                    # Re-assign ranks to ensure they're sequential
                    for i, article in enumerate(articles, 1):
                        article.rank = i
                    
                    # Log score distribution for monitoring
                    if articles:
                        scores = [a.relevance_score for a in articles]
                        print(f"Score distribution: min={min(scores):.1f}, max={max(scores):.1f}, "
                              f"avg={sum(scores)/len(scores):.1f}, range={max(scores)-min(scores):.1f}")
                
                return articles
                
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
