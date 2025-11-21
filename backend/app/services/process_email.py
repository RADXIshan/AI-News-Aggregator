import logging
import html
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from app.agent.email_agent import EmailAgent, RankedArticleDetail, EmailDigestResponse
from app.agent.curator_agent import CuratorAgent
from app.profiles.user_profile import get_user_profile
from app.database.repository import Repository
from app.services.email_service import EmailService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def generate_email_digest(hours: int = 24, top_n: int = 10) -> EmailDigestResponse:
    user_profile = get_user_profile()
    curator = CuratorAgent(user_profile)
    email_agent = EmailAgent(user_profile)
    repo = Repository()
    
    digests = repo.get_recent_digests(hours=hours)
    total = len(digests)
    
    if total == 0:
        logger.warning(f"No digests found from the last {hours} hours")
        raise ValueError("No digests available")
    
    logger.info(f"Ranking {total} digests for email generation")
    ranked_articles = curator.rank_digests(digests)
    
    if not ranked_articles:
        logger.error("Failed to rank digests")
        raise ValueError("Failed to rank articles")
    
    logger.info(f"Generating email digest with top {top_n} articles")
    
    article_details = [
        RankedArticleDetail(
            digest_id=a.digest_id,
            rank=a.rank,
            relevance_score=a.relevance_score,
            reasoning=a.reasoning,
            title=next((d["title"] for d in digests if d["id"] == a.digest_id), ""),
            summary=next((d["summary"] for d in digests if d["id"] == a.digest_id), ""),
            url=next((d["url"] for d in digests if d["id"] == a.digest_id), ""),
            article_type=next((d["article_type"] for d in digests if d["id"] == a.digest_id), "")
        )
        for a in ranked_articles
    ]
    
    email_digest = email_agent.create_email_digest_response(
        ranked_articles=article_details,
        total_ranked=len(ranked_articles),
        limit=top_n
    )
    
    logger.info("Email digest generated successfully")
    logger.info(f"\n=== Email Introduction ===")
    logger.info(email_digest.introduction.greeting)
    logger.info(f"\n{email_digest.introduction.introduction}")
    
    return email_digest


def digest_to_html(digest_response: EmailDigestResponse) -> str:
    """
    Convert EmailDigestResponse to beautiful HTML email
    """
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # Build articles HTML
    articles_html = []
    for idx, article in enumerate(digest_response.articles, 1):
        article_html = f"""
        <div class="article">
            <div class="article-number">#{idx}</div>
            <h2 class="article-title">{html.escape(article.title)}</h2>
            <div class="article-meta">
                <span class="article-type">{html.escape(article.article_type.upper())}</span>
                <span class="article-score">Relevance: {article.relevance_score:.1f}/10</span>
            </div>
            <p class="article-summary">{html.escape(article.summary)}</p>
            <a href="{html.escape(article.url)}" class="read-more">Read Full Article →</a>
        </div>
        """
        articles_html.append(article_html)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 650px;
                margin: 0 auto;
                padding: 0;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: #ffffff;
                margin: 20px;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0 0 10px 0;
                font-size: 28px;
                font-weight: 700;
            }}
            .header .date {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .content {{
                padding: 30px;
            }}
            .greeting {{
                font-size: 18px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 15px;
            }}
            .introduction {{
                font-size: 16px;
                color: #4a4a4a;
                margin-bottom: 30px;
                line-height: 1.7;
            }}
            .article {{
                background: #f9fafb;
                border-left: 4px solid #667eea;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                position: relative;
            }}
            .article-number {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: #667eea;
                color: white;
                width: 36px;
                height: 36px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                font-weight: 700;
                line-height: 1;
            }}
            .article-title {{
                font-size: 18px;
                font-weight: 600;
                color: #1a1a1a;
                margin: 0 40px 10px 0;
                line-height: 1.4;
            }}
            .article-meta {{
                display: flex;
                gap: 15px;
                margin-bottom: 12px;
                font-size: 13px;
            }}
            .article-type {{
                background: #e0e7ff;
                color: #4c51bf;
                padding: 3px 10px;
                border-radius: 12px;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 11px;
            }}
            .article-score {{
                color: #666;
                font-weight: 500;
            }}
            .article-summary {{
                color: #4a4a4a;
                margin: 12px 0;
                line-height: 1.6;
            }}
            .read-more {{
                display: inline-block;
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                font-size: 14px;
                margin-top: 8px;
            }}
            .read-more:hover {{
                text-decoration: underline;
            }}
            .footer {{
                background: #f9fafb;
                padding: 25px 30px;
                text-align: center;
                color: #666;
                font-size: 13px;
                border-top: 1px solid #e5e5e5;
            }}
            .footer p {{
                margin: 5px 0;
            }}
            .footer a {{
                color: #667eea;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI News Digest</h1>
                <div class="date">{current_date}</div>
            </div>
            <div class="content">
                <div class="greeting">{html.escape(digest_response.introduction.greeting)}</div>
                <div class="introduction">{html.escape(digest_response.introduction.introduction)}</div>
                
                {''.join(articles_html)}
            </div>
            <div class="footer">
                <p>You're receiving this because you subscribed to AI News Digest.</p>
                <p>© 2025 AI News Digest. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content


def send_digest_email(hours: int = 24, top_n: int = 10) -> dict:
    """
    Generate and send email digest to all active subscribers
    
    Args:
        hours: Number of hours to look back for digests
        top_n: Number of top articles to include
    
    Returns:
        dict: Result summary with success status and details
    """
    try:
        # Get all active subscribers
        repo = Repository()
        subscribers = repo.get_all_emails(active_only=True)
        
        if not subscribers:
            logger.warning("No active subscribers found")
            return {
                "success": False,
                "error": "No active subscribers"
            }
        
        # Get ranked articles once (same for all users)
        logger.info("Generating base digest data...")
        user_profile = get_user_profile()  # Use default profile for ranking
        curator = CuratorAgent(user_profile)
        
        digests = repo.get_recent_digests(hours=hours)
        total = len(digests)
        
        if total == 0:
            logger.warning(f"No digests found from the last {hours} hours")
            return {
                "success": False,
                "error": "No digests available"
            }
        
        logger.info(f"Ranking {total} digests for email generation")
        ranked_articles = curator.rank_digests(digests)
        
        if not ranked_articles:
            logger.error("Failed to rank digests")
            return {
                "success": False,
                "error": "Failed to rank articles"
            }
        
        # Create article details
        article_details = [
            RankedArticleDetail(
                digest_id=a.digest_id,
                rank=a.rank,
                relevance_score=a.relevance_score,
                reasoning=a.reasoning,
                title=next((d["title"] for d in digests if d["id"] == a.digest_id), ""),
                summary=next((d["summary"] for d in digests if d["id"] == a.digest_id), ""),
                url=next((d["url"] for d in digests if d["id"] == a.digest_id), ""),
                article_type=next((d["article_type"] for d in digests if d["id"] == a.digest_id), "")
            )
            for a in ranked_articles
        ][:top_n]
        
        # Send personalized email to each subscriber
        email_service = EmailService()
        current_date = datetime.now().strftime('%B %d, %Y')
        subject = f"Your Daily AI News Digest - {current_date} 📰"
        
        sent_count = 0
        failed_count = 0
        
        for subscriber in subscribers:
            try:
                # Get personalized user profile for this subscriber
                personalized_profile = get_user_profile(email=subscriber.email)
                email_agent = EmailAgent(personalized_profile)
                
                # Generate personalized introduction
                digest_response = email_agent.create_email_digest_response(
                    ranked_articles=article_details,
                    total_ranked=len(ranked_articles),
                    limit=top_n
                )
                
                # Convert to HTML with personalized greeting
                html_content = digest_to_html(digest_response)
                
                # Send email
                success = email_service.send_digest_email(
                    to_email=subscriber.email,
                    subject=subject,
                    html_content=html_content
                )
                
                if success:
                    sent_count += 1
                    logger.info(f"✓ Sent personalized digest to {subscriber.email} ({personalized_profile['name']})")
                else:
                    failed_count += 1
                    logger.error(f"✗ Failed to send to {subscriber.email}")
                    
            except Exception as e:
                logger.error(f"Error sending to {subscriber.email}: {str(e)}")
                failed_count += 1
        
        if sent_count > 0:
            logger.info(f"✓ Digest sent to {sent_count}/{len(subscribers)} subscribers")
            return {
                "success": True,
                "subject": subject,
                "articles_count": len(article_details),
                "recipients": sent_count,
                "failed": failed_count
            }
        else:
            logger.error("Failed to send digest to any subscribers")
            return {
                "success": False,
                "error": "Failed to send emails to any subscribers"
            }
            
    except ValueError as e:
        logger.error(f"Error generating digest: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    result = send_digest_email(hours=24, top_n=10)
    if result["success"]:
        print("\n=== Email Digest Sent ===")
        print(f"Subject: {result['subject']}")
        print(f"Articles: {result['articles_count']}")
    else:
        print(f"Error: {result['error']}")

