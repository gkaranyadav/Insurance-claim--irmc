import streamlit as st
from streamlit_authenticator import Authenticate
import bcrypt
from datetime import datetime, timedelta
import jwt
from typing import Optional, Dict, Any
import requests
from oauthlib.oauth2 import WebApplicationClient
import json

from database import db
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SECRET_KEY, GOOGLE_DISCOVERY_URL

class InsuranceAuthenticator:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.google_client = WebApplicationClient(GOOGLE_CLIENT_ID)
        
    def generate_token(self, user_data: Dict[str, Any]) -> str:
        """Generate JWT token for session"""
        payload = {
            "user_id": user_data["id"],
            "email": user_data["email"],
            "role": user_data["role"],
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            st.error("Session expired. Please login again.")
            return None
        except jwt.InvalidTokenError:
            st.error("Invalid session. Please login again.")
            return None
    
    def email_password_login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Handle email/password login"""
        user = db.verify_user(email, password)
        if user:
            user["token"] = self.generate_token(user)
            db.update_user_last_login(user["id"])
            return user
        return None
    
    def google_login(self, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Handle Google OAuth login"""
        try:
            # Get token from Google
            token_url, headers, body = self.google_client.prepare_token_request(
                "https://oauth2.googleapis.com/token",
                authorization_response=redirect_uri,
                code=code,
                client_secret=GOOGLE_CLIENT_SECRET
            )
            
            token_response = requests.post(
                token_url,
                headers=headers,
                data=body,
                auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
            )
            
            self.google_client.parse_request_body_response(json.dumps(token_response.json()))
            
            # Get user info
            userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"
            uri, headers, body = self.google_client.add_token(userinfo_endpoint)
            userinfo_response = requests.get(uri, headers=headers, data=body)
            
            if userinfo_response.status_code == 200:
                user_info = userinfo_response.json()
                
                # Create or update user in database
                db.create_google_user(
                    email=user_info["email"],
                    google_id=user_info["sub"],
                    full_name=user_info.get("name", user_info["email"])
                )
                
                # Get user from database
                user = db.get_user_by_google_id(user_info["sub"])
                if user:
                    user["token"] = self.generate_token(user)
                    db.update_user_last_login(user["id"])
                    return user
            return None
        except Exception as e:
            st.error(f"Google login error: {e}")
            return None
    
    def register_user(self, email: str, password: str, full_name: str, 
                     policy_number: Optional[str] = None) -> bool:
        """Register new user"""
        if db.create_user(email, password, full_name, policy_number):
            st.success("Registration successful! Please login.")
            return True
        else:
            st.error("Email already exists or registration failed.")
            return False

# Initialize authenticator
authenticator = InsuranceAuthenticator()
