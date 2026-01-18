import streamlit as st
from database import db  # Now uses Databricks database

class InsuranceAuthenticator:
    def __init__(self):
        self.secret_key = "your-secret-key"  # From config
        
    def authenticate(self, identifier: str, password: str = None) -> dict:
        """Authenticate using REAL Databricks data"""
        # For now, we'll use identifier only (EmployeeID, Email, or PolicyNumber)
        # In production, add password check
        
        user = db.authenticate_user(identifier)
        
        if user:
            # For MVP: Accept any identifier (no password check)
            # Later: Add password/Google OAuth
            
            st.session_state.authenticated = True
            st.session_state.user = user
            st.success(f"Welcome back, {user['first_name']}!")
            return user
        else:
            st.error("User not found in database. Please check your Employee ID, Email, or Policy Number.")
            return None
authenticator = InsuranceAuthenticator()
