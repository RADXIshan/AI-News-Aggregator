from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database.repository import Repository
from app.services.email_service import EmailService
import logging
import os 
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI News Digest API", version="1.0.0")

CLIENT_URL = os.getenv("CLIENT_URL", "http://localhost:5173")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SubscribeRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class SubscribeResponse(BaseModel):
    success: bool
    message: str
    email: str


@app.get("/")
async def root():
    return {"message": "AI News Digest API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/subscribe", response_model=SubscribeResponse)
async def subscribe(request: SubscribeRequest):
    """
    Subscribe a user to the daily AI news digest.
    Sends a confirmation email immediately upon successful registration.
    """
    from app.database.connection import get_session
    
    session = get_session()
    try:
        repo = Repository(session=session)
        
        existing = repo.get_email_by_address(request.email)
        if existing:
            if existing.is_active == "true":
                return SubscribeResponse(
                    success=False,
                    message="This email is already subscribed to our digest.",
                    email=request.email
                )
            else:
                # Reactivate the email
                repo.update_email_status(request.email, True)
                logger.info(f"Reactivated subscription for {request.email}")
                
                # Send confirmation email
                email_service = EmailService()
                email_sent = email_service.send_confirmation_email(
                    to_email=request.email,
                    name=request.name or "there"
                )
                
                return SubscribeResponse(
                    success=True,
                    message="Welcome back! Your subscription has been reactivated. Check your email for confirmation.",
                    email=request.email
                )
        
        # Create new subscription
        email_record = repo.create_email(
            email=request.email,
            name=request.name,
            is_active=True
        )
        
        if not email_record:
            raise HTTPException(status_code=500, detail="Failed to create subscription")
        
        logger.info(f"New subscription created for {request.email}")
        
        # Send confirmation email
        email_service = EmailService()
        email_sent = email_service.send_confirmation_email(
            to_email=request.email,
            name=request.name or "there"
        )
        
        if not email_sent:
            logger.warning(f"Confirmation email failed to send to {request.email}")
        
        return SubscribeResponse(
            success=True,
            message="Successfully subscribed! Check your email for confirmation.",
            email=request.email
        )
        
    except Exception as e:
        logger.error(f"Error during subscription: {str(e)}")
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        session.close()


@app.get("/api/subscribers/count")
async def get_subscriber_count():
    """Get the total number of active subscribers"""
    from app.database.connection import get_session
    
    session = get_session()
    try:
        repo = Repository(session=session)
        subscribers = repo.get_all_emails(active_only=True)
        return {"count": len(subscribers)}
    except Exception as e:
        logger.error(f"Error getting subscriber count: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get subscriber count")
    finally:
        session.close()


class UnsubscribeRequest(BaseModel):
    email: EmailStr


class UnsubscribeResponse(BaseModel):
    success: bool
    message: str
    email: str


@app.post("/api/unsubscribe", response_model=UnsubscribeResponse)
async def unsubscribe(request: UnsubscribeRequest):
    """
    Unsubscribe a user from the daily AI news digest.
    Completely removes the email from the database.
    """
    from app.database.connection import get_session
    
    session = get_session()
    try:
        repo = Repository(session=session)
        
        # Check if email exists
        existing = repo.get_email_by_address(request.email)
        if not existing:
            return UnsubscribeResponse(
                success=False,
                message="This email address is not subscribed to our digest.",
                email=request.email
            )
        
        # Delete the email from database
        deleted = repo.delete_email(request.email)
        
        if deleted:
            logger.info(f"Deleted email from database: {request.email}")
            return UnsubscribeResponse(
                success=True,
                message="Successfully unsubscribed. We're sorry to see you go!",
                email=request.email
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to delete subscription")
        
    except Exception as e:
        logger.error(f"Error during unsubscription: {str(e)}")
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        session.close()


@app.post("/api/trigger-daily-digest")
async def trigger_daily_digest():
    """
    Trigger the daily digest pipeline manually.
    This endpoint is designed to be called by cron jobs.
    """
    from app.daily_runner import run_daily_pipeline
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    logger.info("Daily digest triggered via API endpoint")
    
    try:
        # Run the pipeline in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                run_daily_pipeline,
                24,  # hours
                10   # top_n
            )
        
        return {
            "success": result.get("success", False),
            "message": "Daily digest pipeline completed",
            "details": {
                "scraping": result.get("scraping", {}),
                "processing": result.get("processing", {}),
                "digests": result.get("digests", {}),
                "email_sent": result.get("success", False),
                "duration_seconds": result.get("duration_seconds", 0)
            }
        }
    except Exception as e:
        logger.error(f"Error triggering daily digest: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to run daily digest: {str(e)}")

