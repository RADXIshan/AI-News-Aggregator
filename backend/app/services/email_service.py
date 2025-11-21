import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.my_email = os.getenv("MY_EMAIL")
        self.app_password = os.getenv("APP_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        if not self.my_email or not self.app_password:
            logger.warning("MY_EMAIL or APP_PASSWORD not found in environment variables")
    
    def send_confirmation_email(self, to_email: str, name: str = "there") -> bool:
        """
        Send a confirmation email to a newly subscribed user using Gmail SMTP
        """
        if not self.my_email or not self.app_password:
            logger.error("Cannot send email: MY_EMAIL or APP_PASSWORD not configured")
            return False
        
        try:
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
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        border-radius: 10px 10px 0 0;
                        text-align: center;
                    }}
                    .content {{
                        background: #f9fafb;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .button {{
                        display: inline-block;
                        background: #667eea;
                        color: white;
                        padding: 12px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        color: #666;
                        font-size: 14px;
                    }}
                    h1 {{
                        margin: 0;
                        font-size: 28px;
                    }}
                    .emoji {{
                        font-size: 48px;
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="emoji">🤖</div>
                    <h1>Welcome to AI News Digest!</h1>
                </div>
                <div class="content">
                    <p>Hey {name},</p>
                    
                    <p>Thanks for subscribing to our daily AI news digest! You're now part of an exclusive community that stays ahead of the curve in artificial intelligence.</p>
                    
                    <p><strong>What to expect:</strong></p>
                    <ul>
                        <li>📰 Daily curated AI news from top sources</li>
                        <li>🎯 Personalized content based on your interests</li>
                        <li>⚡ Quick summaries to save you time</li>
                        <li>🔗 Direct links to full articles and videos</li>
                    </ul>
                    
                    <p>Your first digest will arrive in your inbox tomorrow morning. Get ready to stay informed!</p>
                    
                    <p>If you have any questions or feedback, feel free to reply to this email.</p>
                    
                    <p>Best regards,<br>
                    <strong>The AI News Digest Team</strong></p>
                </div>
                <div class="footer">
                    <p>You're receiving this because you subscribed to AI News Digest.</p>
                    <p>© 2025 AI News Digest. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Welcome to AI News Digest! 🤖"
            msg['From'] = self.my_email
            msg['To'] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send via Gmail SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.my_email, self.app_password)
                server.send_message(msg)
            
            logger.info(f"Confirmation email sent to {to_email} via Gmail SMTP")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send confirmation email to {to_email}: {str(e)}")
            return False
    
    def send_digest_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Send the daily digest email using Gmail SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self.my_email or not self.app_password:
            logger.error("Cannot send email: MY_EMAIL or APP_PASSWORD not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.my_email
            msg['To'] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send via Gmail SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.my_email, self.app_password)
                server.send_message(msg)
            
            logger.info(f"Digest email sent to {to_email} via Gmail SMTP")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send digest email to {to_email}: {str(e)}")
            return False
    
    def send_digest_to_all_subscribers(self, subject: str, html_content: str) -> dict:
        """
        Send digest email to all active subscribers
        
        Args:
            subject: Email subject line
            html_content: HTML content of the email
        
        Returns:
            dict: Summary of sending results with success/failure counts
        """
        from app.database.repository import Repository
        
        repo = Repository()
        subscribers = repo.get_all_emails(active_only=True)
        
        if not subscribers:
            logger.warning("No active subscribers found in database")
            return {
                "success": False,
                "total": 0,
                "sent": 0,
                "failed": 0,
                "error": "No active subscribers"
            }
        
        sent_count = 0
        failed_count = 0
        
        for subscriber in subscribers:
            try:
                success = self.send_digest_email(
                    to_email=subscriber.email,
                    subject=subject,
                    html_content=html_content
                )
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error sending to {subscriber.email}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Digest sent to {sent_count}/{len(subscribers)} subscribers ({failed_count} failed)")
        
        return {
            "success": sent_count > 0,
            "total": len(subscribers),
            "sent": sent_count,
            "failed": failed_count
        }
