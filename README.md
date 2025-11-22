# 🤖 AI News Aggregator

An intelligent, automated news aggregation system that scrapes, processes, and curates AI-related content from multiple sources, then delivers personalized daily digests via email. Features a beautiful web interface for user subscriptions with instant email confirmation.

> **🌐 Live Demo:** [https://ai-news-aggregator-digest.vercel.app](https://ai-news-aggregator-digest.vercel.app)

> **📧 Email Service:** Uses Gmail SMTP for reliable email delivery to any recipient. No domain verification required!

## 📸 Screenshots

### Homepage
![Homepage](frontend/src/assets/home.png)
*Beautiful, modern landing page with hero section and feature highlights*

### Subscription Form
![Subscription Form](frontend/src/assets/subform.png)
*User-friendly subscription form with real-time validation*

### Email Confirmation
![Email Confirmation](frontend/src/assets/mail.png)
*Instant email confirmation sent to new subscribers*

## 📰 Content Sources

The aggregator scrapes from **9 diverse AI news sources**:

| Source | Type | Content |
|--------|------|---------|
| **YouTube** | Video | AI channels with transcript extraction |
| **OpenAI Blog** | RSS | Official OpenAI news and updates |
| **Anthropic** | RSS (3 feeds) | News, Research, Engineering |
| **Google AI** | RSS | Google AI blog content |
| **HuggingFace Blog** | RSS | ML/AI tutorials and announcements |
| **HuggingFace Papers** | Web Scraping | Trending research papers |
| **TechCrunch AI** | RSS | AI industry news and startups |
| **MIT Technology Review** | RSS | In-depth AI analysis |
| **VentureBeat AI** | RSS | AI business and enterprise news |

---

## ✨ Features

### Web Subscription System
- Beautiful, responsive React frontend with modern UI/UX
- User-friendly subscription form with real-time validation
- Instant email confirmation upon registration
- Built with React 19, Tailwind CSS 4, and Vite

### FastAPI Backend
- RESTful API for subscription management
- CORS-enabled for frontend integration
- Automatic email confirmation sending
- Subscriber count tracking
- Production-ready with Uvicorn

### Multi-Source Aggregation (9 Sources)
- **YouTube channels** - AI videos with transcript extraction
- **OpenAI Blog** - Official OpenAI news and updates (RSS)
- **Anthropic** - 3 feeds: News, Research, Engineering (RSS with markdown)
- **Google AI** - Google AI blog content (RSS with markdown)
- **HuggingFace Blog** - ML/AI tutorials and announcements (RSS with markdown)
- **HuggingFace Papers** - Trending research papers (web scraping)
- **TechCrunch AI** - AI industry news and startups (RSS with markdown)
- **MIT Technology Review** - In-depth AI analysis (RSS with markdown)
- **VentureBeat AI** - AI business and enterprise news (RSS with markdown)

### AI-Powered Processing
- Intelligent content summarization using Google Gemini
- Personalized content ranking based on user profiles
- Automated digest generation for all articles

### Smart Curation
- Relevance scoring (0-10 scale) based on user interests
- Customizable ranking algorithms
- Top-N article selection for daily digests

### Email Delivery
- Automated daily email digests
- Instant confirmation emails for new subscribers
- Personalized introductions
- Clean, readable HTML formatting
- Multi-recipient support with activation/deactivation

### Robust Data Management
- PostgreSQL database for persistent storage
- Duplicate detection and prevention
- Comprehensive article metadata tracking

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [API Reference](#-api-reference)
- [Deployment](#-deployment)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)

**Quick Links:**
- 📝 [Quick Reference Card](QUICK_REFERENCE.md) - Essential commands and configs
- 📧 [Resend Integration Guide](RESEND_INTEGRATION.md) - Detailed email setup

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL database (Neon, Supabase, or local)
- Google Gemini API key
- Gmail account with App Password (free, no domain needed!)

### 5-Minute Setup

1. **Clone and install dependencies:**
```bash
git clone <repository-url>
cd ai-news-aggregator
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your credentials:
# - Get Gemini API key from https://makersuite.google.com/app/apikey
# - Use your Gmail and App Password (see setup guide below)
# - Update DATABASE_URL with your PostgreSQL connection string
```

3. **Initialize database:**
```bash
python3 -m app.database.init_db
```

4. **Start the application:**
```bash
# Terminal 1 - Backend
python start_api.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

5. **Visit http://localhost:5173** and subscribe!

---

## 📦 Installation

### Backend Setup

```bash
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Database Setup

**Option 1: Cloud Database (Recommended)**

Use Neon, Supabase, or another PostgreSQL provider:
```bash
# Set DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require

# Initialize tables
python3 -m app.database.init_db
```

**Option 2: Local PostgreSQL**

```bash
# Install PostgreSQL, then:
createdb ai_news_aggregator
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_news_aggregator
python3 -m app.database.init_db
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with the following configuration:

```env
# AI News Digest - Environment Variables
# Copy this file to .env and fill in your actual values

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
# PostgreSQL connection string (recommended for Neon, Supabase, etc.)
# Format: postgresql://username:password@host:port/database?sslmode=require
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require

# Alternative: Individual PostgreSQL parameters (fallback if DATABASE_URL not set)
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgres
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=ai_news_aggregator

# ============================================================================
# AI CONFIGURATION
# ============================================================================
# Google Gemini API Key
# Get from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# ============================================================================
# EMAIL CONFIGURATION (Gmail SMTP)
# ============================================================================
# Your Gmail address
MY_EMAIL=your_email@gmail.com

# Gmail App Password (NOT your regular password!)
# Setup guide:
# 1. Enable 2-factor authentication: https://myaccount.google.com/security
# 2. Generate App Password: https://myaccount.google.com/apppasswords
# 3. Use the 16-character password here
APP_PASSWORD=your_16_char_app_password

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# ============================================================================
# NOTES
# ============================================================================
# 1. Never commit this file with real values to version control
# 2. Keep your API keys and passwords secure
# 3. Use different values for development and production
# 4. Gmail free tier: 500 emails/day (plenty for most newsletters!)
# 5. No domain verification needed - works immediately!
```

**Important Notes:**
- Use your Gmail address for `MY_EMAIL`
- Generate an App Password (NOT your regular Gmail password) - see setup guide above
- Gmail allows 500 emails/day on free tier - perfect for newsletters!
- No domain verification needed - works immediately!
- Get your Gemini API key for free from Google AI Studio

### Frontend Configuration

Create `frontend/.env`:

```env
VITE_BASE_URL=http://localhost:8000
```

### User Profile

Customize your interests in `app/profiles/user_profile.py`:

```python
USER_PROFILE = {
    "interests": [
        "Large Language Models",
        "Computer Vision",
        "Reinforcement Learning",
        # Add your interests
    ],
    "technical_level": "advanced",
    "focus_areas": ["research", "applications", "tools"]
}
```

### Content Sources

Add YouTube channels in `app/config.py`:

```python
YOUTUBE_CHANNELS = [
    "UCn8ujwUInbJkBhffxqAPBVQ",  # Channel ID
    # Add more channels
]
```

---

## 💻 Usage

### Web Interface

The web interface provides a beautiful subscription experience:

1. Start both servers:
```bash
python start_api.py  # Terminal 1
cd frontend && npm run dev  # Terminal 2
```

2. Visit http://localhost:5173
3. Users can subscribe with their email
4. They receive instant confirmation emails

### Command Line

**Run the complete daily pipeline:**
```bash
python main.py
```

**With custom parameters:**
```bash
# Scrape last 48 hours, send top 15 articles
python main.py 48 15
```

**Manage email recipients:**
```bash
# Add a recipient
python app/manage_emails.py add john@example.com "John Doe"

# List all recipients
python app/manage_emails.py list

# Activate/deactivate
python app/manage_emails.py activate john@example.com
python app/manage_emails.py deactivate john@example.com

# Delete a recipient
python app/manage_emails.py delete john@example.com
```

### Pipeline Stages

The main pipeline executes 6 stages:

1. **Scraping**: Fetch new content from all sources
2. **Anthropic Processing**: Extract full markdown from articles
3. **Google Processing**: Extract full markdown from articles
4. **YouTube Processing**: Extract transcripts from videos
5. **Digest Generation**: Create AI summaries for all content
6. **Email Delivery**: Rank, curate, and send personalized digest

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + Vite)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │     Hero     │  │ Subscribe    │  │   Features   │          │
│  │   Component  │  │     Form     │  │   Component  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────┬──────────────────────────────────────┘
                            │ POST /api/subscribe
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Uvicorn)                   │
│  • POST /api/subscribe                                           │
│  • GET  /api/subscribers/count                                   │
│  • GET  /health                                                  │
└───────────────────────────┬──────────────────┬───────────────────┘
                            │                  │
                            ▼                  ▼
              ┌─────────────────────┐  ┌─────────────────────┐
              │   DATABASE          │  │   EMAIL SERVICE     │
              │   (PostgreSQL)      │  │   (Resend)          │
              └─────────────────────┘  └─────────────────────┘
                            ▲
                            │
┌───────────────────────────┴───────────────────────────────────────┐
│                    CONTENT PIPELINE (Python)                       │
│  1. Scraping → 2. Processing → 3. AI Agents → 4. Email Delivery  │
└────────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
ai-news-aggregator/
├── app/
│   ├── agent/              # AI agents for processing
│   │   ├── curator_agent.py    # Content ranking & curation
│   │   ├── digest_agent.py     # Summary generation
│   │   └── email_agent.py      # Email content creation
│   ├── database/           # Data layer
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── repository.py       # Data access layer
│   │   ├── connection.py       # Database connection
│   │   └── init_db.py          # Database initialization
│   ├── scrapers/           # Content scrapers (9 sources)
│   │   ├── youtube.py          # YouTube channel scraper
│   │   ├── openai.py           # OpenAI blog scraper
│   │   ├── anthropic.py        # Anthropic blog scraper (3 feeds)
│   │   ├── google.py           # Google AI blog scraper
│   │   ├── huggingface.py      # HuggingFace blog scraper
│   │   ├── huggingface_papers.py # HuggingFace papers scraper
│   │   ├── techcrunch.py       # TechCrunch AI scraper
│   │   ├── mittr.py            # MIT Technology Review scraper
│   │   └── venturebeat.py      # VentureBeat AI scraper
│   ├── services/           # Business logic
│   │   ├── email_service.py    # Email service (Resend)
│   │   └── process_*.py        # Content processors
│   ├── profiles/           # User profiles
│   │   └── user_profile.py     # User preferences & interests
│   ├── api.py              # FastAPI application
│   ├── config.py           # Configuration
│   ├── runner.py           # Scraper orchestration
│   └── daily_runner.py     # Main pipeline
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── utils/          # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── main.py                 # Entry point
├── start_api.py            # FastAPI server startup
├── manage_emails.py        # Email management CLI
└── requirements.txt        # Python dependencies
```

### Database Schema

```sql
-- Users/Subscribers
emails
├── id (PK)
├── email (UNIQUE)
├── name
├── is_active
└── created_at

-- Content Tables (9 sources)
youtube_videos, openai_articles, anthropic_articles, google_articles,
huggingface_articles, huggingface_papers, techcrunch_articles,
mittr_articles, venturebeat_articles
├── id/guid (PK)
├── title
├── url
├── content/transcript/markdown
└── published_at

-- Processed Content
digests
├── id (PK)
├── article_type
├── article_id
├── title
├── summary
└── created_at
```

---

## 📡 API Reference

### Endpoints

**Subscribe a new user:**
```bash
POST /api/subscribe
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe"  # optional
}

Response: {
  "success": true,
  "message": "Successfully subscribed! Check your email for confirmation.",
  "email": "user@example.com"
}
```

**Get subscriber count:**
```bash
GET /api/subscribers/count

Response: {
  "count": 42
}
```

**Health check:**
```bash
GET /health

Response: {
  "status": "healthy"
}
```

### JavaScript Example

```javascript
async function subscribe(email, name) {
  const response = await fetch('http://localhost:8000/api/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, name }),
  });
  return response.json();
}
```

### Python Example

```python
import requests

response = requests.post(
    'http://localhost:8000/api/subscribe',
    json={'email': 'user@example.com', 'name': 'John Doe'}
)
print(response.json())
```

### Gmail SMTP Email Example

The email service uses Gmail SMTP in this format:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create message
msg = MIMEMultipart('alternative')
msg['Subject'] = "Hello World"
msg['From'] = "your_email@gmail.com"
msg['To'] = "recipient@example.com"

# Add HTML content
html_part = MIMEText("<p>Congrats on sending your <strong>first email</strong>!</p>", 'html')
msg.attach(html_part)

# Send via Gmail SMTP
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login("your_email@gmail.com", "your_app_password")
    server.send_message(msg)
```

This is already implemented in `app/services/email_service.py` for both confirmation and digest emails.

### Interactive Documentation

Visit http://localhost:8000/docs for Swagger UI with interactive API testing.

---

## 🚀 Deployment

### Backend Deployment

**Option 1: Railway / Render / Fly.io**

Create a `Procfile`:
```
web: uvicorn app.api:app --host 0.0.0.0 --port $PORT
```

Set environment variables and deploy.

**Option 2: Docker**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option 3: VPS**

```bash
# Install dependencies
sudo apt update && sudo apt install python3-pip nginx

# Clone and setup
git clone <repo-url>
cd ai-news-aggregator
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/ai-news-api.service
```

### Frontend Deployment

**Vercel (Recommended):**
1. Push to GitHub
2. Import project in Vercel
3. Set root directory to `frontend`
4. Add environment variable: `VITE_BASE_URL=https://your-api-domain.com`
5. Deploy

**Netlify:**
```bash
cd frontend
npm run build
# Deploy dist/ folder
```

### Email Service Setup

**Gmail SMTP (Recommended - Free & Easy):**
1. Enable 2-factor authentication: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Add to environment variables:
   ```
   MY_EMAIL=your_email@gmail.com
   APP_PASSWORD=your_16_char_app_password
   ```
4. Done! No domain verification needed, works immediately!

### Background Jobs

**Cron (Linux/macOS):**
```bash
crontab -e
# Add: 0 8 * * * cd /path/to/project && python main.py
```

**GitHub Actions:**
```yaml
name: Daily Digest
on:
  schedule:
    - cron: '0 8 * * *'
jobs:
  send-digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run pipeline
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
        run: python main.py
```

### Cost Estimates

**Free Tier:**
- Backend: Railway/Render free tier
- Frontend: Vercel/Netlify free tier
- Database: Neon free tier
- Email: Resend free tier (100 emails/day)
- **Total: $0/month**

**Production (1000 subscribers):**
- Backend: $5-10/month
- Frontend: Free
- Database: $10-20/month
- Email: $20/month
- **Total: ~$35-50/month**

---

## 🛠️ Development

### Adding a New Content Source

1. Create a scraper in `app/scrapers/new_source.py`
2. Add a model in `app/database/models.py`
3. Update repository in `app/database/repository.py`
4. Register in `SCRAPER_REGISTRY` in `app/runner.py`
5. Add processing service in `app/services/`

### Testing

**Test database connection:**
```bash
python -m app.database.check_connection
```

**Test email service:**
```bash
# Quick Resend test
python test_resend.py

# Full email service test
python test_email_service.py
```

**Verify setup:**
```bash
python verify_setup.py
```

### AI Agents

**Digest Agent**: Generates concise summaries
- Model: Gemini 2.5 Flash
- Output: Title + 2-3 sentence summary

**Curator Agent**: Ranks content by relevance
- Model: Gemini 2.5 Flash
- Scoring: 0-10 scale based on user profile

**Email Agent**: Creates personalized email content
- Model: Gemini 2.5 Flash
- Output: Greeting + introduction + article list

### Email Service (Gmail SMTP)

The application uses Gmail SMTP for all email delivery. Simple, reliable, and works immediately!

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create message
msg = MIMEMultipart('alternative')
msg['Subject'] = "Hello World"
msg['From'] = "your_email@gmail.com"
msg['To'] = "user@example.com"

# Add HTML content
html_part = MIMEText("<p>Your <strong>email content</strong> here</p>", 'html')
msg.attach(html_part)

# Send via Gmail SMTP
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login("your_email@gmail.com", "your_app_password")
    server.send_message(msg)
```

**Key Features:**
- ✅ Send to ANY email address (no domain verification!)
- ✅ Instant confirmation emails for new subscribers
- ✅ Daily digest emails with beautiful HTML formatting
- ✅ Batch sending to all active subscribers
- ✅ 500 emails/day free tier (plenty for newsletters!)
- ✅ Comprehensive error handling and logging

**Setup Gmail App Password:**
1. Enable 2-factor authentication: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Add to `.env`: `APP_PASSWORD=your_16_char_password`

**Implementation:**
- Located in `app/services/email_service.py`
- Used by both the API (`app/api.py`) and pipeline (`app/daily_runner.py`)
- Supports both confirmation and digest email types

**Testing:**
```bash
# Quick test
python test_resend.py

# Full test with database integration
python test_email_service.py
```

---

## 🔍 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
lsof -i :8000
kill -9 <PID>
```

**Package errors:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Port already in use:**
```bash
lsof -i :5173
kill -9 <PID>
```

**Dependencies:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database Issues

**Connection failed:**
```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Reinitialize
python -m app.database.init_db
```

### Email Issues

**Not sending:**
1. Verify MY_EMAIL and APP_PASSWORD are correct in `.env`
2. Make sure you're using an App Password, NOT your regular Gmail password
3. Check 2-factor authentication is enabled on your Google account
4. Look at backend logs for errors
5. Test with: `python test_email_service.py`

**Common Gmail SMTP errors:**
- `535 Authentication failed`: Wrong App Password or 2FA not enabled
- `534 Application-specific password required`: Use App Password, not regular password
- `Connection refused`: Check firewall/network settings

**Setup App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and your device
3. Copy the 16-character password
4. Add to `.env`: `APP_PASSWORD=xxxx xxxx xxxx xxxx` (spaces optional)

### CORS Errors

1. Ensure backend is on port 8000
2. Ensure frontend is on port 5173
3. Check CORS settings in `app/api.py`

---

## 📊 Pipeline Output Example

```
============================================================
Starting Daily AI News Aggregator Pipeline
============================================================

[1/9] Scraping articles from sources...
✓ Scraped 28 total articles from all sources

[2/9] Processing Anthropic markdown...
✓ Processed 2 Anthropic articles (0 failed)

[3/9] Processing Google markdown...
✓ Processed 4 Google articles (0 failed)

[4/9] Processing HuggingFace markdown...
✓ Processed 0 HuggingFace articles (0 failed)

[5/9] Processing TechCrunch markdown...
✓ Processed 4 TechCrunch articles (0 failed)

[6/9] Processing MIT TR markdown...
✓ Processed 0 MIT TR articles (0 failed)

[7/9] Processing VentureBeat markdown...
✓ Processed 1 VentureBeat articles (0 failed)

[8/9] Processing YouTube transcripts...
✓ Processed 5 transcripts (0 unavailable)

[9/9] Creating digests and sending email...
✓ Created 20 digests (0 failed out of 20 total)
✓ Email sent successfully with 10 articles

============================================================
Pipeline Summary
============================================================
Duration: 45.3 seconds
Scraped: 28 articles from 9 sources
Processed: 28 articles
Digests: 20 created
Email: Sent to 5 subscribers
============================================================
```

---

## 📝 Dependencies

### Core Dependencies

- `sqlalchemy` - Database ORM
- `psycopg2-binary` - PostgreSQL adapter
- `google-genai` - Google Gemini API
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `resend` - Email delivery
- `beautifulsoup4` - HTML parsing
- `feedparser` - RSS feed parsing
- `youtube-transcript-api` - YouTube transcripts
- `pydantic` - Data validation
- `python-dotenv` - Environment management

### Frontend Dependencies

- `react` - UI framework
- `vite` - Build tool
- `tailwindcss` - Styling

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional content sources
- Enhanced ranking algorithms
- UI/dashboard for monitoring
- Webhook support for real-time updates
- Multi-language support
- Advanced filtering options
- Unsubscribe functionality
- User preference management
- Analytics dashboard

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

Built with:
- Google Gemini for AI processing
- Resend for email delivery
- Neon for PostgreSQL hosting
- FastAPI for the backend
- React for the frontend

---

## 📞 Support

For issues or questions:
- Run `python verify_setup.py` to check configuration
- Check logs for error messages
- Verify environment variables are set correctly
- Test database connection
- Ensure API keys are valid

---

---

## 📊 Content Sources Summary

**9 Active Sources:**
- 8 RSS feeds (fast, reliable)
- 1 web scraper (HuggingFace Papers)
- Covers: Company blogs, research, news outlets, video content

**Performance:**
- Scraping: 5-10 seconds for all sources
- No JavaScript rendering needed
- Low maintenance overhead
- Excellent content diversity

---

**Built with ❤️ for the AI community**

Get started now: `python start_api.py` and visit http://localhost:5173
