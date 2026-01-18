import streamlit as st
from database import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class InsuranceAuthenticator:
    def __init__(self):
        self.secret_key = "insurance-secret-key-2024"
        
    def test_connection(self):
        """Test database connection"""
        return db.test_connection()
        
    def authenticate(self, identifier: str) -> dict:
        """Authenticate using REAL Databricks data"""
        logger.info(f"🔐 Attempting authentication for: {identifier}")
        
        if not identifier or identifier.strip() == "":
            st.error("❌ Please enter Employee ID, Email, or Policy Number")
            return None
        
        # Clean the identifier
        identifier = identifier.strip()
        
        # Show connection test first
        with st.spinner("Testing database connection..."):
            success, message = self.test_connection()
            if not success:
                st.error(f"❌ Database connection failed: {message}")
                return None
            else:
                st.info(f"✅ {message}")
        
        # Now authenticate
        with st.spinner(f"Searching for {identifier} in insurance database..."):
            user = db.authenticate_user(identifier)
            
            if user:
                logger.info(f"✅ Authentication successful for: {user['email']}")
                
                # Store in session
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.user_id = user['employee_id']
                
                # Show success
                st.success(f"✅ Welcome, {user['first_name']} {user['last_name']}!")
                st.balloons()
                
                return user
            else:
                logger.warning(f"❌ Authentication failed for: {identifier}")
                return None

# Initialize authenticator
authenticator = InsuranceAuthenticator()
