import os
from typing import Optional

# Google OAuth Configuration
# Get these from Google Cloud Console: https://console.cloud.google.com/
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# App Configuration
APP_NAME = "SecureClaim AI Insurance Portal"
APP_DESCRIPTION = "AI-Powered Insurance Claim Processing System"
SECRET_KEY = os.environ.get("STREAMLIT_SECRET_KEY", "insurance-claim-auth-secret-key-2024")

# Database
DATABASE_URL = "sqlite:///users.db"

# Session config
SESSION_TIMEOUT_MINUTES = 30
MAX_LOGIN_ATTEMPTS = 5
