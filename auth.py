def authenticate(self, identifier: str) -> dict:
    """Authenticate using REAL Databricks data"""
    logger.info(f"🔐 Attempting authentication for: {identifier}")
    
    if not identifier or identifier.strip() == "":
        st.error("❌ Please enter Employee ID, Email, or Policy Number")
        return None
    
    # Clean the identifier
    identifier = identifier.strip()
    
    # Show we're connecting
    with st.spinner(f"Searching for {identifier} in insurance database..."):
        user = db.authenticate_user(identifier)  # This now uses the FIXED method
        
        if user:
            logger.info(f"✅ Authentication successful for: {user['email']}")
            
            # Store in session
            st.session_state.authenticated = True
            st.session_state.user = user
            st.session_state.user_id = user['employee_id']
            
            # Auto-redirect
            st.session_state.page = "dashboard"
            st.rerun()
            
            return user
        else:
            logger.warning(f"❌ Authentication failed for: {identifier}")
            return None
