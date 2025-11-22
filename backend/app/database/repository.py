from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import (
    YouTubeVideo, OpenAIArticle, AnthropicArticle, GoogleArticle, Digest, Email,
    MetaArticle, MistralArticle, HuggingFaceArticle, 
    HuggingFacePaper, TechCrunchArticle, MITTRArticle, VentureBeatArticle
)
from .connection import get_session
import uuid


class Repository:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
    
    def create_youtube_video(self, video_id: str, title: str, url: str, channel_id: str, 
                            published_at: datetime, description: str = "", transcript: Optional[str] = None) -> Optional[YouTubeVideo]:
        existing = self.session.query(YouTubeVideo).filter_by(video_id=video_id).first()
        if existing:
            return None
        video = YouTubeVideo(
            video_id=video_id,
            title=title,
            url=url,
            channel_id=channel_id,
            published_at=published_at,
            description=description,
            transcript=transcript
        )
        self.session.add(video)
        self.session.commit()
        return video
    
    def create_openai_article(self, guid: str, title: str, url: str, published_at: datetime,
                              description: str = "", category: Optional[str] = None) -> Optional[OpenAIArticle]:
        existing = self.session.query(OpenAIArticle).filter_by(guid=guid).first()
        if existing:
            return None
        article = OpenAIArticle(
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            description=description,
            category=category
        )
        self.session.add(article)
        self.session.commit()
        return article
    
    def create_anthropic_article(self, guid: str, title: str, url: str, published_at: datetime,
                                description: str = "", category: Optional[str] = None) -> Optional[AnthropicArticle]:
        existing = self.session.query(AnthropicArticle).filter_by(guid=guid).first()
        if existing:
            return None
        article = AnthropicArticle(
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            description=description,
            category=category
        )
        self.session.add(article)
        self.session.commit()
        return article
    
    def bulk_create_youtube_videos(self, videos: List[dict]) -> int:
        new_videos = []
        for v in videos:
            existing = self.session.query(YouTubeVideo).filter_by(video_id=v["video_id"]).first()
            if not existing:
                new_videos.append(YouTubeVideo(
                    video_id=v["video_id"],
                    title=v["title"],
                    url=v["url"],
                    channel_id=v.get("channel_id", ""),
                    published_at=v["published_at"],
                    description=v.get("description", ""),
                    transcript=v.get("transcript")
                ))
        if new_videos:
            self.session.add_all(new_videos)
            self.session.commit()
        return len(new_videos)
    
    def bulk_create_openai_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(OpenAIArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(OpenAIArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def bulk_create_anthropic_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(AnthropicArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(AnthropicArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def create_google_article(self, guid: str, title: str, url: str, published_at: datetime,
                             description: str = "", category: Optional[str] = None) -> Optional[GoogleArticle]:
        existing = self.session.query(GoogleArticle).filter_by(guid=guid).first()
        if existing:
            return None
        article = GoogleArticle(
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            description=description,
            category=category
        )
        self.session.add(article)
        self.session.commit()
        return article
    
    def bulk_create_google_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(GoogleArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(GoogleArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def get_anthropic_articles_without_markdown(self, limit: Optional[int] = None) -> List[AnthropicArticle]:
        query = self.session.query(AnthropicArticle).filter(AnthropicArticle.markdown.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update_anthropic_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(AnthropicArticle).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            self.session.commit()
            return True
        return False
    
    def get_google_articles_without_markdown(self, limit: Optional[int] = None) -> List[GoogleArticle]:
        query = self.session.query(GoogleArticle).filter(GoogleArticle.markdown.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update_google_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(GoogleArticle).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            self.session.commit()
            return True
        return False
    
    def get_youtube_videos_without_transcript(self, limit: Optional[int] = None) -> List[YouTubeVideo]:
        query = self.session.query(YouTubeVideo).filter(YouTubeVideo.transcript.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update_youtube_video_transcript(self, video_id: str, transcript: str) -> bool:
        video = self.session.query(YouTubeVideo).filter_by(video_id=video_id).first()
        if video:
            video.transcript = transcript
            self.session.commit()
            return True
        return False
    
    def get_articles_without_digest(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        articles = []
        seen_ids = set()
        
        digests = self.session.query(Digest).all()
        for d in digests:
            seen_ids.add(f"{d.article_type}:{d.article_id}")
        
        youtube_videos = self.session.query(YouTubeVideo).filter(
            YouTubeVideo.transcript.isnot(None),
            YouTubeVideo.transcript != "__UNAVAILABLE__"
        ).all()
        for video in youtube_videos:
            key = f"youtube:{video.video_id}"
            if key not in seen_ids:
                articles.append({
                    "type": "youtube",
                    "id": video.video_id,
                    "title": video.title,
                    "url": video.url,
                    "content": video.transcript or video.description or "",
                    "published_at": video.published_at
                })
        
        openai_articles = self.session.query(OpenAIArticle).all()
        for article in openai_articles:
            key = f"openai:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "openai",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.description or "",
                    "published_at": article.published_at
                })
        
        anthropic_articles = self.session.query(AnthropicArticle).filter(
            AnthropicArticle.markdown.isnot(None)
        ).all()
        for article in anthropic_articles:
            key = f"anthropic:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "anthropic",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.markdown or article.description or "",
                    "published_at": article.published_at
                })
        
        google_articles = self.session.query(GoogleArticle).filter(
            GoogleArticle.markdown.isnot(None)
        ).all()
        for article in google_articles:
            key = f"google:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "google",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.markdown or article.description or "",
                    "published_at": article.published_at
                })
        
        # Meta articles
        meta_articles = self.session.query(MetaArticle).filter(
            MetaArticle.markdown.isnot(None)
        ).all()
        for article in meta_articles:
            key = f"meta:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "meta",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.markdown or article.description or "",
                    "published_at": article.published_at
                })
        
# Mistral articles
        mistral_articles = self.session.query(MistralArticle).filter(
            MistralArticle.markdown.isnot(None)
        ).all()
        for article in mistral_articles:
            key = f"mistral:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "mistral",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.markdown or article.description or "",
                    "published_at": article.published_at
                })
        
        # HuggingFace articles
        huggingface_articles = self.session.query(HuggingFaceArticle).filter(
            HuggingFaceArticle.markdown.isnot(None)
        ).all()
        for article in huggingface_articles:
            key = f"huggingface:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "huggingface",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.markdown or article.description or "",
                    "published_at": article.published_at
                })
        
        # HuggingFace papers
        huggingface_papers = self.session.query(HuggingFacePaper).all()
        for paper in huggingface_papers:
            key = f"huggingface_papers:{paper.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "huggingface_papers",
                    "id": paper.guid,
                    "title": paper.title,
                    "url": paper.url,
                    "content": paper.description or "",
                    "published_at": paper.published_at
                })
        
        # TechCrunch articles
        techcrunch_articles = self.session.query(TechCrunchArticle).filter(
            TechCrunchArticle.markdown.isnot(None)
        ).all()
        for article in techcrunch_articles:
            key = f"techcrunch:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "techcrunch",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.markdown or article.description or "",
                    "published_at": article.published_at
                })
        
        # MITTR articles
        mittr_articles = self.session.query(MITTRArticle).filter(
            MITTRArticle.markdown.isnot(None)
        ).all()
        for article in mittr_articles:
            key = f"mittr:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "mittr",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.markdown or article.description or "",
                    "published_at": article.published_at
                })
        
        # VentureBeat articles
        venturebeat_articles = self.session.query(VentureBeatArticle).filter(
            VentureBeatArticle.markdown.isnot(None)
        ).all()
        for article in venturebeat_articles:
            key = f"venturebeat:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "venturebeat",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.markdown or article.description or "",
                    "published_at": article.published_at
                })
        
        if limit:
            articles = articles[:limit]
        
        return articles
    
    def create_digest(self, article_type: str, article_id: str, url: str, title: str, summary: str, published_at: Optional[datetime] = None) -> Optional[Digest]:
        digest_id = f"{article_type}:{article_id}"
        existing = self.session.query(Digest).filter_by(id=digest_id).first()
        if existing:
            return None
        
        if published_at:
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            created_at = published_at
        else:
            created_at = datetime.now(timezone.utc)
        
        digest = Digest(
            id=digest_id,
            article_type=article_type,
            article_id=article_id,
            url=url,
            title=title,
            summary=summary,
            created_at=created_at
        )
        self.session.add(digest)
        self.session.commit()
        return digest
    
    def get_recent_digests(self, hours: int = 24) -> List[Dict[str, Any]]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        digests = self.session.query(Digest).filter(
            Digest.created_at >= cutoff_time
        ).order_by(Digest.created_at.desc()).all()
        
        return [
            {
                "id": d.id,
                "article_type": d.article_type,
                "article_id": d.article_id,
                "url": d.url,
                "title": d.title,
                "summary": d.summary,
                "created_at": d.created_at
            }
            for d in digests
        ]


    def create_email(self, email: str, name: Optional[str] = None, is_active: bool = True) -> Optional[Email]:
        """Create a new email recipient"""
        existing = self.session.query(Email).filter_by(email=email).first()
        if existing:
            return None
        
        email_record = Email(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            is_active="true" if is_active else "false"
        )
        self.session.add(email_record)
        self.session.commit()
        return email_record
    
    def get_all_emails(self, active_only: bool = True) -> List[Email]:
        """Get all email recipients"""
        query = self.session.query(Email)
        if active_only:
            query = query.filter_by(is_active="true")
        return query.all()
    
    def get_email_by_address(self, email: str) -> Optional[Email]:
        """Get an email recipient by email address"""
        return self.session.query(Email).filter_by(email=email).first()
    
    def update_email_status(self, email: str, is_active: bool) -> bool:
        """Update the active status of an email recipient"""
        email_record = self.session.query(Email).filter_by(email=email).first()
        if email_record:
            email_record.is_active = "true" if is_active else "false"
            self.session.commit()
            return True
        return False
    
    def delete_email(self, email: str) -> bool:
        """Delete an email recipient"""
        email_record = self.session.query(Email).filter_by(email=email).first()
        if email_record:
            self.session.delete(email_record)
            self.session.commit()
            return True
        return False

    # Meta Articles
    def bulk_create_meta_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(MetaArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(MetaArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def get_meta_articles_without_markdown(self, limit: Optional[int] = None) -> List[MetaArticle]:
        query = self.session.query(MetaArticle).filter(MetaArticle.markdown.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update_meta_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(MetaArticle).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            self.session.commit()
            return True
        return False

# Mistral Articles
    def bulk_create_mistral_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(MistralArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(MistralArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def get_mistral_articles_without_markdown(self, limit: Optional[int] = None) -> List[MistralArticle]:
        query = self.session.query(MistralArticle).filter(MistralArticle.markdown.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update_mistral_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(MistralArticle).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            self.session.commit()
            return True
        return False

    # HuggingFace Articles
    def bulk_create_huggingface_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(HuggingFaceArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(HuggingFaceArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def get_huggingface_articles_without_markdown(self, limit: Optional[int] = None) -> List[HuggingFaceArticle]:
        query = self.session.query(HuggingFaceArticle).filter(HuggingFaceArticle.markdown.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update_huggingface_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(HuggingFaceArticle).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            self.session.commit()
            return True
        return False

    # HuggingFace Papers
    def bulk_create_huggingface_papers(self, papers: List[dict]) -> int:
        new_papers = []
        for p in papers:
            existing = self.session.query(HuggingFacePaper).filter_by(guid=p["guid"]).first()
            if not existing:
                new_papers.append(HuggingFacePaper(
                    guid=p["guid"],
                    title=p["title"],
                    url=p["url"],
                    published_at=p["published_at"],
                    description=p.get("description", ""),
                    upvotes=str(p.get("upvotes", ""))
                ))
        if new_papers:
            self.session.add_all(new_papers)
            self.session.commit()
        return len(new_papers)

    # TechCrunch Articles
    def bulk_create_techcrunch_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(TechCrunchArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(TechCrunchArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def get_techcrunch_articles_without_markdown(self, limit: Optional[int] = None) -> List[TechCrunchArticle]:
        query = self.session.query(TechCrunchArticle).filter(TechCrunchArticle.markdown.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update_techcrunch_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(TechCrunchArticle).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            self.session.commit()
            return True
        return False

    # MITTR Articles
    def bulk_create_mittr_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(MITTRArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(MITTRArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def get_mittr_articles_without_markdown(self, limit: Optional[int] = None) -> List[MITTRArticle]:
        query = self.session.query(MITTRArticle).filter(MITTRArticle.markdown.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update_mittr_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(MITTRArticle).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            self.session.commit()
            return True
        return False

    # VentureBeat Articles
    def bulk_create_venturebeat_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(VentureBeatArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(VentureBeatArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def get_venturebeat_articles_without_markdown(self, limit: Optional[int] = None) -> List[VentureBeatArticle]:
        query = self.session.query(VentureBeatArticle).filter(VentureBeatArticle.markdown.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update_venturebeat_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(VentureBeatArticle).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            self.session.commit()
            return True
        return False
