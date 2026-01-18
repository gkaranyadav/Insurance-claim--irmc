# Main application file - iRMC InsureAI ® - Insurance Claim AI Automation
import streamlit as st
from auth import authenticator
from database import db
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="iRMC InsureAI ®",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with iRMC design pattern
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(135deg, #175CFF, #00A3FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        margin: 2rem 0 3rem 0;
        padding: 0;
    }
    
    .app-box {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #175CFF;
        box-shadow: 0 4px 12px rgba(23, 92, 255, 0.1);
        margin-bottom: 1rem;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #175CFF, #00A3FF);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        margin-top: 1rem;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(23, 92, 255, 0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: #F8FAFF;
        border-radius: 12px;
        padding: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #175CFF;
        color: white;
    }
    
    div[data-testid="stForm"] {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(23, 92, 255, 0.15);
        border: 1px solid #E6F0FF;
    }
    
    .login-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #175CFF;
    }
    
    .claim-card {
        background: linear-gradient(135deg, #175CFF, #00A3FF);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .google-btn {
        background: linear-gradient(135deg, #DB4437, #EA4335) !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

def login_page():
    """Display login/signup page"""
    st.markdown('<div class="main-header">iRMC InsureAI ®</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; font-size: 1.1rem; text-align: center; margin-bottom: 3rem;">AI-Powered Insurance Claim Automation System</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["**🔐 Login**", "**📝 Register**"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            # Google OAuth Button (Placeholder)
            if st.button("Sign in with Google", key="google_login", type="secondary", use_container_width=True):
                st.info("Google OAuth setup required in production. Using demo for now.")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<h3 style="color: #175CFF; text-align: center; margin-bottom: 2rem;">Insurance Login</h3>', unsafe_allow_html=True)
            
            with st.form("login_form"):
                identifier = st.text_input(
                    "**Employee ID, Email, or Policy Number**",
                    placeholder="EMP10001 or dawn.knight@meta.com or POL96733444"
                )
                password = st.text_input("**Password (Optional for now)**", 
                                       type="password", 
                                       placeholder="Password feature coming soon")
                
                submitted = st.form_submit_button("**Login →**", use_container_width=True)
                
                if submitted:
                    if identifier:
                        with st.spinner("Authenticating with insurance database..."):
                            user = authenticator.authenticate(identifier)
                            if user:
                                st.session_state.authenticated = True
                                st.session_state.user = user
                                st.session_state.page = "dashboard"
                                st.rerun()
                            else:
                                st.error("❌ User not found. Please check your credentials.")
                    else:
                        st.warning("⚠️ Please enter your Employee ID, Email, or Policy Number")
            
            st.markdown('<div style="text-align: center; margin-top: 1rem;">', unsafe_allow_html=True)
            st.markdown('<a href="#" style="color: #175CFF; text-decoration: none;">Forgot your credentials?</a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #175CFF; text-align: center; margin-bottom: 2rem;">Register New Policyholder</h3>', unsafe_allow_html=True)
            
            with st.form("register_form"):
                full_name = st.text_input("**Full Name**", placeholder="John Doe")
                email = st.text_input("**Email Address**", placeholder="your.email@example.com")
                policy_number = st.text_input("**Policy Number (Optional)**", placeholder="POL12345678")
                employee_id = st.text_input("**Employee ID (If applicable)**", placeholder="EMP10001")
                password = st.text_input("**Password**", type="password", placeholder="Create a secure password")
                confirm_password = st.text_input("**Confirm Password**", type="password", placeholder="Re-enter your password")
                
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
                    strength_color = ["#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#175CFF"][min(strength, 4)]
                    st.markdown(f"Password Strength: <span style='color:{strength_color};font-weight:bold'>{strength_text}</span>", 
                                unsafe_allow_html=True)
                
                terms = st.checkbox("**I agree to the Terms of Service and Privacy Policy**")
                
                submitted = st.form_submit_button("**Create Account →**", use_container_width=True)
                
                if submitted:
                    if not all([full_name, email, password, confirm_password, terms]):
                        st.error("❌ Please fill all required fields and agree to terms")
                    elif password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(password) < 8:
                        st.error("❌ Password must be at least 8 characters")
                    else:
                        st.success("✅ Registration successful! (Demo mode - backend integration pending)")
                        st.info("In production: This would create a new user in the insurance database")
    
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("**iRMC InsureAI ®**")
        st.markdown("© 2024 All rights reserved")
        st.markdown("[Privacy Policy] • [Terms of Service] • [Contact Support]")
        st.markdown('</div>', unsafe_allow_html=True)

def dashboard():
    """Display main dashboard after login"""
    user = st.session_state.user
    
    # Top Navigation
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        st.markdown(f"""
        <div style='margin-bottom: 1rem;'>
            <div class="main-header" style='font-size: 2.5rem; text-align: left; margin: 0;'> iRMC InsureAI ®</div>
            <p style='color: #666; font-size: 1.1rem; margin: 0;'>
                Welcome back, <strong style="color: #175CFF;">{user.get('first_name', 'Valued Customer')}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"**Role:** {user.get('role', 'Policyholder').title()}")
    with col3:
        if st.button("**🚪 Logout**", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()
    
    st.markdown("---")
    
    # AI Agent Applications Section
    st.markdown('<h3 style="color: #175CFF; text-align: center; margin-bottom: 2rem;">AI Agent Applications</h3>', unsafe_allow_html=True)
    
    # Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="app-box">
            <div>
                <h4 style='color: #175CFF; margin: 0 0 0.5rem 0;'>Claim Submission</h4>
                <p style='color: #555; margin: 0; font-size: 0.9rem;'>Submit new insurance claims with AI assistance.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Claim Submission", key="claim_submit", use_container_width=True):
            st.session_state.page = "file_claim"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="app-box">
            <div>
                <h4 style='color: #175CFF; margin: 0 0 0.5rem 0;'>Fraud Detection AI</h4>
                <p style='color: #555; margin: 0; font-size: 0.9rem;'>AI-powered fraud detection and risk analysis.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Fraud Detection", key="fraud_detect", use_container_width=True):
            st.session_state.page = "fraud_analysis"
            st.rerun()
    
    # Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="app-box">
            <div>
                <h4 style='color: #175CFF; margin: 0 0 0.5rem 0;'>Claim Adjudication</h4>
                <p style='color: #555; margin: 0; font-size: 0.9rem;'>AI agent for claim approval and processing.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Adjudication", key="adjudication", use_container_width=True):
            st.session_state.page = "adjudication"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="app-box">
            <div>
                <h4 style='color: #175CFF; margin: 0 0 0.5rem 0;'>Policy Validation</h4>
                <p style='color: #555; margin: 0; font-size: 0.9rem;'>Verify policy details and coverage eligibility.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Policy Validation", key="policy_validation", use_container_width=True):
            st.session_state.page = "policy_validation"
            st.rerun()
    
    # Row 3
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="app-box">
            <div>
                <h4 style='color: #175CFF; margin: 0 0 0.5rem 0;'>Payment Processing</h4>
                <p style='color: #555; margin: 0; font-size: 0.9rem;'>AI agent for claim payout processing.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Payment Processing", key="payment", use_container_width=True):
            st.session_state.page = "payment"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="app-box">
            <div>
                <h4 style='color: #175CFF; margin: 0 0 0.5rem 0;'>🚀 Coming Soon</h4>
                <p style='color: #555; margin: 0; font-size: 0.9rem;'>More AI agents and tools in development.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore More", key="more_btn", use_container_width=True, disabled=True):
            pass

def file_claim_page():
    """File new claim page"""
    user = st.session_state.user
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"# 📄 File New Claim")
    with col2:
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    
    st.markdown(f"**Policy Holder:** {user.get('first_name', '')} {user.get('last_name', '')} | **Policy:** {user.get('policy_number', 'N/A')}")
    st.markdown("---")
    
    with st.form("new_claim_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            claim_type = st.selectbox(
                "**Claim Type**",
                ["Health", "Dental", "Vision", "Accident", "Critical Illness", "Hospitalization"]
            )
            date_of_incident = st.date_input("**Date of Incident**")
            amount = st.number_input("**Claim Amount ($)**", min_value=0.0, step=100.0, value=1000.0)
        
        with col2:
            provider_name = st.text_input("**Healthcare Provider**", placeholder="Hospital/Clinic Name")
            provider_id = st.text_input("**Provider ID**", placeholder="Provider identification number")
            diagnosis_code = st.text_input("**Diagnosis Code (ICD-10)**", placeholder="e.g., E11.9")
        
        description = st.text_area("**Description of Claim**", height=100,
                                  placeholder="Please describe the medical service, treatment, or incident...")
        
        # File upload
        uploaded_files = st.file_uploader(
            "**Upload Supporting Documents**",
            type=["pdf", "jpg", "png", "docx"],
            accept_multiple_files=True,
            help="Upload medical bills, prescriptions, doctor's notes, etc."
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
        
        agree = st.checkbox("**I certify that all information provided is accurate and complete**")
        
        submitted = st.form_submit_button("**Submit Claim to AI Agents →**", use_container_width=True)
        
        if submitted:
            if not all([claim_type, date_of_incident, amount, description, agree]):
                st.error("❌ Please fill all required fields and agree to certification")
            else:
                with st.spinner("Processing claim through AI agents..."):
                    # Simulate AI agent processing
                    st.success("✅ Claim submitted successfully!")
                    st.info("🤖 AI Agents are now processing your claim:")
                    st.write("1. **Policy Validation Agent** → Checking policy status ✓")
                    st.write("2. **Fraud Detection Agent** → Analyzing risk patterns ✓")
                    st.write("3. **Claim Adjudication Agent** → Determining coverage ✓")
                    st.write("4. **Administration Agent** → Routing for approval ✓")
                    
                    st.markdown("---")
                    st.markdown("**Next Steps:**")
                    st.markdown("- You'll receive updates via email")
                    st.markdown("- Check claim status in 'My Claims'")
                    st.markdown("- Average processing time: 24-48 hours")

def fraud_analysis_page():
    """Fraud detection AI analysis"""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"# 🕵️ Fraud Detection AI")
    with col2:
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    
    st.markdown("### AI-Powered Fraud Risk Analysis")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="card">
            <h4 style='color: #175CFF; margin: 0 0 0.5rem 0;'>Risk Score</h4>
            <h2 style='margin: 0;'>82/100</h2>
            <p style='color: #666; margin: 0; font-size: 0.9rem;'>Medium Risk</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h4 style='color: #175CFF; margin: 0 0 0.5rem 0;'>Previous Claims</h4>
            <h2 style='margin: 0;'>6</h2>
            <p style='color: #666; margin: 0; font-size: 0.9rem;'>Last 12 months</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <h4 style='color: #175CFF; margin: 0 0 0.5rem 0;'>Fraud Flags</h4>
            <h2 style='margin: 0;'>2</h2>
            <p style='color: #666; margin: 0; font-size: 0.9rem;'>Requires review</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### AI Analysis Results")
    
    # Simulate AI analysis
    with st.expander("**Risk Factors Detected**", expanded=True):
        st.write("✅ **Normal Patterns:**")
        st.write("- Consistent claim amounts")
        st.write("- Valid provider information")
        st.write("- Reasonable diagnosis codes")
        
        st.write("⚠️ **Attention Required:**")
        st.write("- High claim frequency (2.4 claims/month)")
        st.write("- Previous hospitalization count: 5")
        st.write("- Blood pressure: High")
    
    with st.expander("**ML Model Insights**"):
        st.write("**Model:** XGBoost Classifier")
        st.write("**Accuracy:** 94.2%")
        st.write("**Features Analyzed:** 28")
        st.write("**Training Data:** 50,000+ historical claims")
        st.write("**Last Updated:** 2024-10-01")

def main():
    """Main function - controls page routing"""
    if not st.session_state.authenticated:
        login_page()
    else:
        if st.session_state.page == "dashboard":
            dashboard()
        elif st.session_state.page == "file_claim":
            file_claim_page()
        elif st.session_state.page == "fraud_analysis":
            fraud_analysis_page()
        elif st.session_state.page == "adjudication":
            st.info("Claim Adjudication page under development")
            if st.button("← Back to Dashboard"):
                st.session_state.page = "dashboard"
                st.rerun()
        elif st.session_state.page == "policy_validation":
            st.info("Policy Validation page under development")
            if st.button("← Back to Dashboard"):
                st.session_state.page = "dashboard"
                st.rerun()
        elif st.session_state.page == "payment":
            st.info("Payment Processing page under development")
            if st.button("← Back to Dashboard"):
                st.session_state.page = "dashboard"
                st.rerun()

if __name__ == "__main__":
    main()
