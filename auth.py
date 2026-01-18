import streamlit as st
from admin_db import admin_db
from database import policyholder_db

class InsuranceAuthenticator:
    def authenticate(self, username: str, password: str = None, is_admin_login: bool = False):
        """Unified authentication for admin and policyholders"""
        
        if is_admin_login:
            # ADMIN LOGIN (SQLite)
            if not username or not password:
                st.error("❌ Admin login requires username and password")
                return None
            
            admin = admin_db.authenticate_admin(username, password)
            if admin:
                st.success(f"✅ Welcome, Admin {admin['full_name']}!")
                return admin
            else:
                st.error("❌ Invalid admin credentials")
                return None
        else:
            # POLICYHOLDER LOGIN (Databricks)
            if not username:
                st.error("❌ Please enter Employee ID, Email, or Policy Number")
                return None
            
            policyholder = policyholder_db.authenticate_policyholder(username)
            if policyholder:
                st.success(f"✅ Welcome, {policyholder['first_name']}!")
                return policyholder
            else:
                st.error("❌ Policyholder not found")
                return None

authenticator = InsuranceAuthenticator()
