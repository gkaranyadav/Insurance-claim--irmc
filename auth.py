import streamlit as st
from database import db

class InsuranceAuthenticator:
    def authenticate(self, identifier: str):
        """Simple authentication"""
        try:
            # Just pass to database
            return db.authenticate_user(identifier)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None

authenticator = InsuranceAuthenticator()
