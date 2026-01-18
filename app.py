import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io

from auth import authenticator
from database import db
from config import APP_NAME, APP_DESCRIPTION, GOOGLE_CLIENT_ID

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #1E3A8A;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    .stButton > button {
        width: 100%;
        background-color: #1E3A8A;
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #1E40AF;
    }
    .google-btn {
        background-color: #DB4437 !important;
    }
    .claim-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "token" not in st.session_state:
    st.session_state.token = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "google_oauth" not in st.session_state:
    st.session_state.google_oauth = False

def show_login_page():
    """Display login/registration page"""
    st.markdown(f"<h1 class='main-header'>{APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>{APP_DESCRIPTION}</p>", unsafe_allow_html=True)
    
    # Create tabs for Login and Register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)# Google OAuth But tif GOOGLE_CLIENT_ID:
                if st.button("Sign in with Google", key="google_login", type="secondary"):
                    # For Streamlit Cloud, we need to set up proper OAuth flow
                    st.info("Google OAuth setup required in production. Using demo for now.")
                    # In production, this would redirect to Google OAuth
                    st.session_state.page = "demo_google"
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Email Login</h3>", unsafe_allow_html=True)
             # Email/Password Form
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your.email@example.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                remember_me = st.checkbox("Remember me")
                
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    if email and password:
                        with st.spinner("Authenticating..."):
                            user = authenticator.email_password_login(email, password)
                            if user:
                                st.session_state.authenticated = True
                                st.session_state.user = user
                                st.session_state.token = user["token"]
                                st.session_state.page = "dashboard"
                                st.rerun()
                            else:
                                st.error("Invalid email or password")
                    else:
                        st.error("Please fill all fields")
            
            st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
            st.markdown("<a href='#' style='color: #1E3A8A;'>Forgot Password?</a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Create Account</h3>", unsafe_allow_html=True)
            
            with st.form("register_form"):
                full_name = st.text_input("Full Name", placeholder="John Doe")
                email = st.text_input("Email", placeholder="your.email@example.com")
                policy_number = st.text_input("Policy Number (Optional)", placeholder="POL12345678")
                password = st.text_input("Password", type="password", placeholder="Create a strong password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
                
                # Password strength indicator
                if password:
                    strength = 0
                    if len(password) >= 8:
                        strength += 1
                    if any(c.isupper() for c in password):
                        strength += 1
                    if any(c.isdigit() for c in password):
                        strength += 1
                    if any(c in "!@#$%^&*" for c in password):
                        strength += 1
                    
                    strength_text = ["Very Weak", "Weak", "Fair", "Good", "Strong"][min(strength, 4)]
                    strength_color = ["#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#1E3A8A"][min(strength, 4)]
                    st.markdown(f"Password Strength: <span style='color:{strength_color};font-weight:bold'>{strength_text}</span>", 
                                unsafe_allow_html=True)
                
                terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
                
                submitted = st.form_submit_button("Create Account")
                
                if submitted:
                    if not all([full_name, email, password, confirm_password]):
                        st.error("Please fill all required fields")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 8:
                        st.error("Password must be at least 8 characters")
                    elif not terms:
                        st.error("You must agree to the terms")
                    else:
                        with st.spinner("Creating account..."):
                            if authenticator.register_user(email, password, full_name, policy_number):
                                st.success("Account created successfully! Please login.")
    
            st.markdown("</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("**SecureClaim AI Insurance**")
        st.markdown("© 2024 All rights reserved")
        st.markdown("[Privacy Policy] • [Terms of Service] • [Contact Support]")
        st.markdown("</div>", unsafe_allow_html=True)

def show_dashboard():
    """Display main dashboard after login"""
    user = st.session_state.user
    
    # Top Navigation
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        st.markdown(f"# Welcome back, {user['full_name']}! 👋")
    with col2:
        st.markdown(f"**Role:** {user['role'].title()}")
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.page = "login"
            st.rerun()
    
    st.markdown("---")
    
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/477/477103.png", width=100)
        st.markdown(f"### {user['email']}")
        st.markdown(f"**Policy:** {user.get('policy_number', 'Not linked')}")
        st.markdown("---")
        
        selected = option_menu(
            menu_title="Navigation",
            options=["Dashboard", "File Claim", "My Claims", "Documents", "Profile"],
            icons=["house", "plus-circle", "file-text", "folder", "person"],
            menu_icon="cast",
            default_index=0
        )
    
    # Main Content based on selection
    if selected == "Dashboard":
        show_dashboard_content(user)
    elif selected == "File Claim":
        show_file_claim(user)
    elif selected == "My Claims":
        show_my_claims(user)
    elif selected == "Documents":
        show_documents(user)
    elif selected == "Profile":
        show_profile(user)

def show_dashboard_content(user):
    """Dashboard content"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Active Policies")
        st.markdown("## 2")
        st.markdown("<small>2 Health, 0 Dental</small>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 💰 Total Coverage")
        st.markdown("## $200,000")
        st.markdown("<small>Max claim: $50,000</small>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📋 Open Claims")
        st.markdown("## 1")
        st.markdown("<small>Under review</small>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### ⏳ Next Premium")
        st.markdown("## Nov 15")
        st.markdown("<small>$420 due</small>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("## 🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ File New Claim", use_container_width=True):
            st.session_state.page = "file_claim"
            st.rerun()
    
    with col2:
        if st.button("📋 Check Status", use_container_width=True):
            st.session_state.page = "my_claims"
            st.rerun()
    
    with col3:
        if st.button("📄 Upload Docs", use_container_width=True):
            st.session_state.page = "documents"
            st.rerun()
    
    with col4:
        if st.button("💳 Make Payment", use_container_width=True):
            st.info("Payment portal coming soon!")
    
    st.markdown("---")
    
    # Recent Activity
    st.markdown("## 📈 Recent Activity")
    
    # Sample claims data
    claims_data = pd.DataFrame({
        "Date": ["2024-10-05", "2024-09-28", "2024-08-15"],
        "Type": ["Dental", "Health", "Vision"],
        "Amount": ["$1,200", "$3,500", "$450"],
        "Status": ["Under Review", "Approved", "Paid"],
        "Status_Color": ["warning", "success", "info"]
    })
    
    # Display claims as cards
    for _, claim in claims_data.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                st.markdown(f"**{claim['Type']} Claim**")
                st.markdown(f"<small>{claim['Date']}</small>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Amount**")
                st.markdown(f"**{claim['Amount']}**")
            with col3:
                status_color = {
                    "Under Review": "orange",
                    "Approved": "green",
                    "Paid": "blue"
                }.get(claim['Status'], "gray")
                st.markdown(f"**Status**")
                st.markdown(f":{status_color}[{claim['Status']}]")
            with col4:
                if st.button("View", key=f"view_{claim['Date']}"):
                    st.info(f"Viewing {claim['Type']} claim details")
            with col5:
                if st.button("Download", key=f"dl_{claim['Date']}"):
                    st.info(f"Downloading {claim['Type']} claim documents")
            st.markdown("---")
    
    # Claims chart
    st.markdown("## 📊 Claims Overview")
    chart_data = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Claims": [3, 5, 2, 4, 6, 3],
        "Approved": [2, 4, 1, 3, 5, 2]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=chart_data["Month"],
        y=chart_data["Claims"],
        name="Total Claims",
        marker_color="#1E3A8A"
    ))
    fig.add_trace(go.Bar(
        x=chart_data["Month"],
        y=chart_data["Approved"],
        name="Approved Claims",
        marker_color="#10B981"
    ))
    fig.update_layout(barmode="group", height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_file_claim(user):
    """File new claim form"""
    st.markdown("# 📄 File New Claim")
    st.markdown("Complete the form below to submit a new insurance claim.")
    
    with st.form("new_claim_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            claim_type = st.selectbox(
                "Claim Type",
                ["Health", "Dental", "Vision", "Accident", "Critical Illness"]
            )
            date_of_incident = st.date_input("Date of Incident")
            amount = st.number_input("Claim Amount ($)", min_value=0.0, step=100.0)
        
        with col2:
            provider_name = st.text_input("Healthcare Provider")
            provider_id = st.text_input("Provider ID")
            diagnosis_code = st.text_input("Diagnosis Code (ICD-10)")
        
        description = st.text_area("Description of Claim", height=100,
                                  placeholder="Please describe the medical service or treatment...")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload Supporting Documents",
            type=["pdf", "jpg", "png", "docx"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.info(f"{len(uploaded_files)} file(s) uploaded")
        
        agree = st.checkbox("I certify that the information provided is accurate and complete")
        
        submitted = st.form_submit_button("Submit Claim")
        
        if submitted:
            if not all([claim_type, date_of_incident, amount, description, agree]):
                st.error("Please fill all required fields and agree to certification")
            else:
                with st.spinner("Submitting claim..."):
                    # Here you would connect to your backend/database
                    st.success("✅ Claim submitted successfully!")
                    st.info("Your claim is now under review. You'll be notified of updates.")

def show_my_claims(user):
    """View existing claims"""
    st.markdown("# 📋 My Claims")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Pending", "Under Review", "Approved", "Denied", "Paid"]
        )
    with col2:
        type_filter = st.selectbox(
            "Filter by Type",
            ["All", "Health", "Dental", "Vision", "Other"]
        )
    with col3:
        date_filter = st.selectbox(
            "Sort by Date",
            ["Newest First", "Oldest First"]
        )
    
    # Claims table (sample data)
    claims_data = pd.DataFrame({
        "ID": ["CLM-001", "CLM-002", "CLM-003"],
        "Type": ["Dental", "Health", "Vision"],
        "Date": ["2024-10-05", "2024-09-28", "2024-08-15"],
        "Amount": ["$1,200", "$3,500", "$450"],
        "Status": ["Under Review", "Approved", "Paid"],
        "Agent": ["AI System", "John Smith", "AI System"],
        "Last Update": ["2 days ago", "1 week ago", "1 month ago"]
    })
    
    # Apply filters
    if status_filter != "All":
        claims_data = claims_data[claims_data["Status"] == status_filter]
    if type_filter != "All":
        claims_data = claims_data[claims_data["Type"] == type_filter]
    
    # Display as expandable cards
    for _, claim in claims_data.iterrows():
        with st.expander(f"{claim['ID']} - {claim['Type']} Claim - {claim['Status']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Amount:** {claim['Amount']}")
                st.markdown(f"**Date:** {claim['Date']}")
            with col2:
                st.markdown(f"**Status:** {claim['Status']}")
                st.markdown(f"**Agent:** {claim['Agent']}")
            with col3:
                st.markdown(f"**Last Update:** {claim['Last Update']}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📄 View Details", key=f"details_{claim['ID']}"):
                    st.info(f"Showing details for {claim['ID']}")
            with col2:
                if st.button("💬 Contact Agent", key=f"contact_{claim['ID']}"):
                    st.info(f"Opening chat with {claim['Agent']}")
            with col3:
                if st.button("📥 Download", key=f"download_{claim['ID']}"):
                    st.info(f"Downloading documents for {claim['ID']}")

def show_documents(user):
    """Document management"""
    st.markdown("# 📁 Documents")
    
    tab1, tab2, tab3 = st.tabs(["Upload Documents", "My Documents", "Templates"])
    
    with tab1:
        st.markdown("### Upload New Documents")
        
        doc_type = st.selectbox(
            "Document Type",
            ["Medical Bill", "Prescription", "Doctor's Note", "Insurance Card", "ID Proof", "Other"]
        )
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "jpg", "png", "jpeg", "docx"],
            key="doc_upload"
        )
        
        if uploaded_file:
            st.success(f"File uploaded: {uploaded_file.name}")
            st.write(f"Size: {uploaded_file.size / 1024:.2f} KB")
            
            if st.button("Submit Document"):
                st.success("Document submitted for processing!")
    
    with tab2:
        st.markdown("### Your Documents")
        
        # Sample documents
        documents = [
            {"name": "Medical_Bill_Oct.pdf", "type": "Medical Bill", "date": "2024-10-05", "size": "1.2 MB"},
            {"name": "Prescription.jpg", "type": "Prescription", "date": "2024-10-01", "size": "450 KB"},
            {"name": "ID_Proof.png", "type": "ID Proof", "date": "2024-09-15", "size": "800 KB"},
        ]
        
        for doc in documents:
            col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
            with col1:
                st.markdown(f"**{doc['name']}**")
                st.markdown(f"<small>{doc['type']} • {doc['date']} • {doc['size']}</small>", unsafe_allow_html=True)
            with col2:
                st.markdown("Verified ✅" if doc['type'] != "ID Proof" else "Pending ⏳")
            with col3:
                if st.button("Download", key=f"dl_{doc['name']}"):
                    st.info(f"Downloading {doc['name']}")
            with col4:
                if st.button("Delete", key=f"del_{doc['name']}"):
                    st.warning(f"Deleting {doc['name']}")
            st.markdown("---")
    
    with tab3:
        st.markdown("### Document Templates")
        st.info("Download templates for common documents")
        
        templates = [
            "Claim Form Template",
            "Medical Authorization Form",
            "Appeal Letter Template",
            "Payment Instruction Form"
        ]
        
        for template in templates:
            if st.button(f"📥 Download {template}", key=f"tmpl_{template}"):
                st.info(f"Downloading {template}")

def show_profile(user):
    """User profile management"""
    st.markdown("# 👤 Profile Settings")
    
    tab1, tab2, tab3 = st.tabs(["Personal Info", "Security", "Notifications"])
    
    with tab1:
        st.markdown("### Personal Information")
        
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name", value=user.get('full_name', ''))
                email = st.text_input("Email", value=user.get('email', ''), disabled=True)
                phone = st.text_input("Phone Number", placeholder="+1-234-567-8900")
            
            with col2:
                policy_number = st.text_input("Policy Number", value=user.get('policy_number', ''))
                dob = st.date_input("Date of Birth")
                address = st.text_input("Address", placeholder="123 Main St, City, State ZIP")
            
            emergency_contact = st.text_input("Emergency Contact")
            emergency_phone = st.text_input("Emergency Phone")
            
            if st.form_submit_button("Update Profile"):
                st.success("Profile updated successfully!")
    
    with tab2:
        st.markdown("### Security Settings")
        
        # Change Password
        with st.expander("Change Password"):
            with st.form("password_form"):
                current = st.text_input("Current Password", type="password")
                new = st.text_input("New Password", type="password")
                confirm = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Update Password"):
                    if new == confirm:
                        st.success("Password updated!")
                    else:
                        st.error("New passwords don't match")
        
        # Two-Factor Authentication
        with st.expander("Two-Factor Authentication"):
            mfa_enabled = st.toggle("Enable 2FA", value=False)
            if mfa_enabled:
                st.info("Scan QR code with authenticator app")
                st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=SecureClaim2FA", width=150)
                verification = st.text_input("Enter 6-digit code")
                if st.button("Verify"):
                    st.success("2FA enabled successfully!")
        
        # Login History
        with st.expander("Login History"):
            st.info("Last login: Today at 10:30 AM")
            st.info("Device: Chrome on Windows")
            st.info("Location: San Francisco, CA")
    
    with tab3:
        st.markdown("### Notification Preferences")
        
        email_notifications = st.checkbox("Email Notifications", value=True)
        sms_notifications = st.checkbox("SMS Notifications", value=False)
        push_notifications = st.checkbox("Push Notifications", value=True)
        
        st.markdown("---")
        st.markdown("#### Notification Types")
        
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Claim Status Updates", value=True)
            st.checkbox("Payment Reminders", value=True)
            st.checkbox("Policy Updates", value=True)
        with col2:
            st.checkbox("Security Alerts", value=True)
            st.checkbox("Promotional Offers", value=False)
            st.checkbox("Newsletter", value=False)
        
        if st.button("Save Preferences"):
            st.success("Notification preferences saved!")

def show_admin_dashboard(user):
    """Admin dashboard (simplified for now)"""
    st.markdown("# ⚙️ Admin Dashboard")
    st.markdown(f"Welcome, System Administrator")
    
    tab1, tab2, tab3 = st.tabs(["Users", "Claims", "System"])
    
    with tab1:
        st.markdown("### User Management")
        # Would show user list, edit roles, etc.
        st.info("User management panel coming soon")
    
    with tab2:
        st.markdown("### Claims Overview")
        # Would show all claims, analytics
        st.info("Claims analytics panel coming soon")
    
    with tab3:
        st.markdown("### System Monitoring")
        st.metric("Active Users", "142")
        st.metric("Pending Claims", "23")
        st.metric("System Uptime", "99.9%")

# Main app routing
def main():
    if not st.session_state.authenticated:
        show_login_page()
    else:
        user = st.session_state.user
        if user["role"] == "admin":
            show_admin_dashboard(user)
        else:
            show_dashboard()

if __name__ == "__main__":
    main()
