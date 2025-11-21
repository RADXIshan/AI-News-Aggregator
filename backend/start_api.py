from app.api import app

# Export app for Vercel serverless
# The variable name must be 'app' for Vercel to detect it
app = app