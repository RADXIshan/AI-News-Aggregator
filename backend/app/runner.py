import logging
from typing import List, Callable, Any
from .config import YOUTUBE_CHANNELS
from .scrapers.youtube import YouTubeScraper, ChannelVideo
from .scrapers.openai import OpenAIScraper
from .scrapers.anthropic import AnthropicScraper
from .scrapers.google import GoogleScraper
from .scrapers.meta import MetaScraper
from .scrapers.mistral import MistralScraper
from .scrapers.huggingface import HuggingFaceScraper
from .scrapers.huggingface_papers import HuggingFacePapersScraper
from .scrapers.techcrunch import TechCrunchScraper
from .scrapers.mittr import MITTRScraper
from .scrapers.venturebeat import VentureBeatScraper
from .database.repository import Repository

logger = logging.getLogger(__name__)


def _save_youtube_videos(
    scraper: YouTubeScraper, repo: Repository, hours: int
) -> List[ChannelVideo]:
    videos = []
    video_dicts = []
    for channel_id in YOUTUBE_CHANNELS:
        channel_videos = scraper.get_latest_videos(channel_id, hours=hours)
        videos.extend(channel_videos)
        video_dicts.extend(
            [
                {
                    "video_id": v.video_id,
                    "title": v.title,
                    "url": v.url,
                    "channel_id": channel_id,
                    "published_at": v.published_at,
                    "description": v.description,
                    "transcript": v.transcript,
                }
                for v in channel_videos
            ]
        )
    if video_dicts:
        repo.bulk_create_youtube_videos(video_dicts)
    return videos


def _save_rss_articles(
    scraper, repo: Repository, hours: int, save_func: Callable
) -> List[Any]:
    articles = scraper.get_articles(hours=hours)
    if articles:
        article_dicts = [
            {
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category,
            }
            for a in articles
        ]
        save_func(article_dicts)
    return articles


def _save_huggingface_papers(
    scraper: HuggingFacePapersScraper, repo: Repository, hours: int
) -> List[Any]:
    papers = scraper.get_papers(hours=hours)
    if papers:
        paper_dicts = [
            {
                "guid": p.guid,
                "title": p.title,
                "url": p.url,
                "published_at": p.published_at,
                "description": p.description,
                "upvotes": p.upvotes,
            }
            for p in papers
        ]
        repo.bulk_create_huggingface_papers(paper_dicts)
    return papers


SCRAPER_REGISTRY = [
    ("youtube", YouTubeScraper(), _save_youtube_videos),
    (
        "openai",
        OpenAIScraper(),
        lambda s, r, h: _save_rss_articles(s, r, h, r.bulk_create_openai_articles),
    ),
    (
        "anthropic",
        AnthropicScraper(),
        lambda s, r, h: _save_rss_articles(s, r, h, r.bulk_create_anthropic_articles),
    ),
    (
        "google",
        GoogleScraper(),
        lambda s, r, h: _save_rss_articles(s, r, h, r.bulk_create_google_articles),
    ),
    # Meta AI - RSS feed not available (404)
    # (
    #     "meta",
    #     MetaScraper(),
    #     lambda s, r, h: _save_rss_articles(s, r, h, r.bulk_create_meta_articles),
    # ),
    # Mistral AI - RSS feed not available (404)
    # (
    #     "mistral",
    #     MistralScraper(),
    #     lambda s, r, h: _save_rss_articles(s, r, h, r.bulk_create_mistral_articles),
    # ),
    (
        "huggingface",
        HuggingFaceScraper(),
        lambda s, r, h: _save_rss_articles(s, r, h, r.bulk_create_huggingface_articles),
    ),
    (
        "huggingface_papers",
        HuggingFacePapersScraper(),
        _save_huggingface_papers,
    ),
    (
        "techcrunch",
        TechCrunchScraper(),
        lambda s, r, h: _save_rss_articles(s, r, h, r.bulk_create_techcrunch_articles),
    ),
    (
        "mittr",
        MITTRScraper(),
        lambda s, r, h: _save_rss_articles(s, r, h, r.bulk_create_mittr_articles),
    ),
    (
        "venturebeat",
        VentureBeatScraper(),
        lambda s, r, h: _save_rss_articles(s, r, h, r.bulk_create_venturebeat_articles),
    ),
]


def run_scrapers(hours: int = 24) -> dict:
    repo = Repository()
    results = {}

    try:
        for name, scraper, save_func in SCRAPER_REGISTRY:
            try:
                items = save_func(scraper, repo, hours)
                results[name] = items
            except Exception as e:
                logger.error(f"Failed to scrape {name}: {e}", exc_info=True)
                results[name] = []
    finally:
        repo.session.close()

    return results


if __name__ == "__main__":
    results = run_scrapers(hours=24)
    print(f"YouTube videos: {len(results['youtube'])}")
    print(f"OpenAI articles: {len(results['openai'])}")
    print(f"Anthropic articles: {len(results['anthropic'])}")
    print(f"Google articles: {len(results['google'])}")
    print(f"HuggingFace articles: {len(results['huggingface'])}")
    print(f"HuggingFace papers: {len(results['huggingface_papers'])}")
    print(f"TechCrunch articles: {len(results['techcrunch'])}")
    print(f"MIT TR articles: {len(results['mittr'])}")
    print(f"VentureBeat articles: {len(results['venturebeat'])}")