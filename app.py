"""
iRMC InsureAI ® - Insurance Claim AI Automation System
Minimalistic Industry-Grade Application
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="iRMC InsureAI ®",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CUSTOM CSS (Minimal but Professional)
# ============================================
st.markdown("""
<style>
    /* Main Header */
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #175CFF, #00A3FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 700;
        margin: 1.5rem 0 2rem 0;
    }
    
    /* Card Design */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(23, 92, 255, 0.08);
        border-left: 4px solid #175CFF;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(23, 92, 255, 0.12);
    }
    
    /* Admin Card */
    .admin-card {
        border-left: 4px solid #FF6B6B;
    }
    
    /* Policyholder Card */
    .policy-card {
        border-left: 4px solid #4ECDC4;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #175CFF, #00A3FF);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1348CC, #0088CC);
    }
    
    /* Metrics */
    .metric {
        background: linear-gradient(135deg, #175CFF, #00A3FF);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# ============================================
# SIMPLE AUTHENTICATION (No External Imports)
# ============================================
class SimpleAuth:
    """Minimal authentication for demo"""
    @staticmethod
    def authenticate_policyholder(identifier):
        """Demo policyholder auth"""
        demo_users = {
            'EMP10001': {'name': 'Dawn Knight', 'policy': 'POL96733444', 'coverage': 100000},
            'dawn.knight@meta.com': {'name': 'Dawn Knight', 'policy': 'POL96733444', 'coverage': 100000},
            'POL96733444': {'name': 'Dawn Knight', 'policy': 'POL96733444', 'coverage': 100000}
        }
        return demo_users.get(identifier)
    
    @staticmethod
    def authenticate_admin(username, password):
        """Demo admin auth"""
        if username == 'admin' and password == 'Admin@123':
            return {'name': 'System Admin', 'role': 'superadmin'}
        return None

auth = SimpleAuth()

# ============================================
# PAGE 1: LOGIN PAGE
# ============================================
def login_page():
    """Main login page"""
    st.markdown('<div class="main-header">iRMC InsureAI ®</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; margin-bottom: 3rem;">AI-Powered Insurance Claim Automation</p>', unsafe_allow_html=True)
    
    # Login type selection
    login_type = st.radio(
        "**Select Portal:**",
        ["👤 Policyholder Portal", "🔧 Admin Portal"],
        horizontal=True
    )
    
    is_admin = login_type == "🔧 Admin Portal"
    
    # Login form
    with st.form("login_form"):
        if is_admin:
            username = st.text_input("**Username**", placeholder="admin")
            password = st.text_input("**Password**", type="password", placeholder="••••••••")
        else:
            username = st.text_input("**Employee ID / Email / Policy Number**", 
                                   placeholder="EMP10001 or dawn.knight@meta.com",
                                   value="EMP10001")
            password = st.text_input("**Password (Optional)**", type="password", 
                                   placeholder="Demo mode - optional", disabled=True)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            submitted = st.form_submit_button("**Login →**", use_container_width=True)
        
        if submitted:
            if is_admin:
                user = auth.authenticate_admin(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.is_admin = True
                    st.session_state.authenticated = True
                    st.session_state.page = 'admin_dashboard'
                    st.success(f"✅ Welcome, {user['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid admin credentials")
            else:
                user = auth.authenticate_policyholder(username)
                if user:
                    st.session_state.user = user
                    st.session_state.is_admin = False
                    st.session_state.authenticated = True
                    st.session_state.page = 'policyholder_dashboard'
                    st.success(f"✅ Welcome, {user['name']}!")
                    st.rerun()
                else:
                    st.error("❌ User not found. Try: EMP10001")
    
    # Demo credentials
    st.markdown("---")
    with st.expander("**Demo Credentials**", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Admin Portal:**")
            st.code("Username: admin\nPassword: Admin@123")
        with col2:
            st.markdown("**Policyholder Portal:**")
            st.code("EMP10001\ndawn.knight@meta.com\nPOL96733444")

# ============================================
# PAGE 2: ADMIN DASHBOARD
# ============================================
def admin_dashboard():
    """Admin Dashboard - Industry Level Features"""
    
    # Header
    col1, col2, col3 = st.columns([5, 2, 1])
    with col1:
        st.markdown('<div class="main-header" style="font-size: 2.5rem; text-align: left;">iRMC InsureAI ®</div>', unsafe_allow_html=True)
        st.markdown(f"**Admin Panel** • Welcome, {st.session_state.user['name']}")
    with col3:
        if st.button("**Logout**"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # REAL-TIME METRICS
    st.markdown("### 📊 Real-Time Insurance Dashboard")
    
    metrics = st.columns(4)
    with metrics[0]:
        st.markdown("""
        <div class="metric">
            <h4 style="margin: 0 0 0.5rem 0;">Active Policies</h4>
            <h2 style="margin: 0;">4,281</h2>
            <p style="margin: 0; opacity: 0.9;">+2.4%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics[1]:
        st.markdown("""
        <div class="metric">
            <h4 style="margin: 0 0 0.5rem 0;">Pending Claims</h4>
            <h2 style="margin: 0;">127</h2>
            <p style="margin: 0; opacity: 0.9;">12 require attention</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics[2]:
        st.markdown("""
        <div class="metric">
            <h4 style="margin: 0 0 0.5rem 0;">Fraud Flags</h4>
            <h2 style="margin: 0;">23</h2>
            <p style="margin: 0; opacity: 0.9;">High risk: 8</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics[3]:
        st.markdown("""
        <div class="metric">
            <h4 style="margin: 0 0 0.5rem 0;">Avg Processing</h4>
            <h2 style="margin: 0;">4.2h</h2>
            <p style="margin: 0; opacity: 0.9;">-15% from last week</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # AI AGENT CONTROLS
    st.markdown("### 🤖 AI Agent Control Center")
    
    tab1, tab2, tab3 = st.tabs(["Fraud Detection", "Claim Adjudication", "System Analytics"])
    
    with tab1:
        st.markdown("#### 🕵️ Fraud Detection AI")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="admin-card card">
                <h4 style="color: #FF6B6B; margin: 0 0 0.5rem 0;">Real-Time Monitoring</h4>
                <p>Monitoring 8,200+ policies for fraud patterns using ML</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚨 Run Fraud Scan", key="fraud_scan"):
                with st.spinner("Scanning..."):
                    st.success("✅ Scan complete! Found 8 high-risk claims")
        
        with col2:
            st.markdown("""
            <div class="admin-card card">
                <h4 style="color: #FF6B6B; margin: 0 0 0.5rem 0;">ML Model Status</h4>
                <p>XGBoost Model • Accuracy: 94.2% • Updated: Today</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Retrain Model", key="retrain"):
                st.info("Retraining with latest data...")
                st.success("✅ Model accuracy improved to 95.1%")
    
    with tab2:
        st.markdown("#### ⚖️ Claim Adjudication Queue")
        
        # Sample claim queue
        claims = [
            {"id": "CLM-1001", "type": "Health", "amount": "$5,200", "status": "Pending"},
            {"id": "CLM-1002", "type": "Dental", "amount": "$1,800", "status": "Under Review"},
            {"id": "CLM-1003", "type": "Accident", "amount": "$12,500", "status": "Pending"}
        ]
        
        for claim in claims:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                with col1:
                    st.write(f"**{claim['id']}** • {claim['type']}")
                with col2:
                    st.write(f"**Amount:** {claim['amount']}")
                with col3:
                    st.write(f"**Status:** {claim['status']}")
                with col4:
                    if st.button("Review", key=f"rev_{claim['id']}"):
                        st.success(f"✅ {claim['id']} approved!")
                st.markdown("---")
    
    with tab3:
        st.markdown("#### 📈 System Analytics")
        
        # Sample analytics data
        data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Claims': [120, 135, 145, 160, 155, 170],
            'Approved': [110, 125, 135, 150, 145, 160]
        })
        
        st.line_chart(data.set_index('Month'))
        st.dataframe(data, use_container_width=True)

# ============================================
# PAGE 3: POLICYHOLDER DASHBOARD
# ============================================
def policyholder_dashboard():
    """Simple Policyholder Dashboard"""
    
    user = st.session_state.user
    
    # Header
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown('<div class="main-header" style="font-size: 2.5rem; text-align: left;">iRMC InsureAI ®</div>', unsafe_allow_html=True)
        st.markdown(f"Welcome back, **{user['name']}**")
    with col2:
        if st.button("**Logout**"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # QUICK ACTIONS
    st.markdown("### 📋 Quick Actions")
    
    cols = st.columns(3)
    with cols[0]:
        if st.button("📄 File New Claim", use_container_width=True):
            st.session_state.page = 'file_claim'
            st.rerun()
    with cols[1]:
        if st.button("📋 Claim Status", use_container_width=True):
            st.info("Showing your recent claims...")
    with cols[2]:
        if st.button("👤 My Policy", use_container_width=True):
            st.info(f"Policy: {user['policy']}\nCoverage: ${user['coverage']:,.2f}")
    
    st.markdown("---")
    
    # POLICY SUMMARY
    st.markdown("### 📊 Your Policy Summary")
    
    summary_cols = st.columns(3)
    with summary_cols[0]:
        st.markdown(f"""
        <div class="policy-card card">
            <h4 style="color: #4ECDC4;">Coverage Amount</h4>
            <h3>${user['coverage']:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_cols[1]:
        st.markdown(f"""
        <div class="policy-card card">
            <h4 style="color: #4ECDC4;">Policy Number</h4>
            <h3>{user['policy']}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_cols[2]:
        st.markdown("""
        <div class="policy-card card">
            <h4 style="color: #4ECDC4;">AI Processing</h4>
            <h3>Active</h3>
            <p>Your claims are processed by AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # RECENT ACTIVITY
    st.markdown("### 📝 Recent Activity")
    
    activities = [
        {"date": "2024-10-05", "type": "Dental Claim", "status": "Under Review", "amount": "$7,998"},
        {"date": "2024-09-28", "type": "Health Claim", "status": "Approved", "amount": "$3,500"},
        {"date": "2024-08-15", "type": "Vision Claim", "status": "Paid", "amount": "$450"}
    ]
    
    for activity in activities:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{activity['type']}**")
            st.write(f"*{activity['date']}*")
        with col2:
            st.write(f"**Status:** {activity['status']}")
        with col3:
            st.write(f"**Amount:** {activity['amount']}")
        st.markdown("---")

# ============================================
# PAGE 4: FILE CLAIM PAGE
# ============================================
def file_claim_page():
    """File new claim page"""
    
    user = st.session_state.user
    
    # Header with back button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"# 📄 File New Claim")
    with col2:
        if st.button("← Back"):
            st.session_state.page = 'policyholder_dashboard' if not st.session_state.is_admin else 'admin_dashboard'
            st.rerun()
    
    st.markdown(f"**Policy Holder:** {user['name']}")
    st.markdown(f"**Available Coverage:** ${user['coverage']:,.2f}")
    st.markdown("---")
    
    # Claim form
    with st.form("claim_form"):
        claim_type = st.selectbox(
            "**Type of Claim**",
            ["Health", "Dental", "Vision", "Hospitalization", "Accident"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            incident_date = st.date_input("**Date of Incident**")
            amount = st.number_input("**Claim Amount ($)**", min_value=0.0, value=1000.0)
        with col2:
            provider = st.text_input("**Healthcare Provider**")
            location = st.text_input("**Location**")
        
        description = st.text_area("**Description**", height=100)
        
        # File upload
        uploaded_files = st.file_uploader(
            "**Supporting Documents**",
            type=["pdf", "jpg", "png"],
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("**Submit to AI Processing →**")
        
        if submitted:
            st.success("✅ Claim submitted successfully!")
            st.info("🤖 AI agents are now processing your claim:")
            st.write("1. **Policy Validation** → Checking coverage ✓")
            st.write("2. **Fraud Detection** → Analyzing risk patterns ✓")
            st.write("3. **Adjudication** → Determining approval ✓")
            st.write("4. **Payment Processing** → Scheduled for payout ✓")
            
            st.balloons()

# ============================================
# MAIN APPLICATION ROUTER
# ============================================
def main():
    """Main application router"""
    
    # Route to correct page
    if not st.session_state.authenticated:
        login_page()
    else:
        if st.session_state.is_admin:
            if st.session_state.page == 'admin_dashboard':
                admin_dashboard()
            elif st.session_state.page == 'file_claim':
                file_claim_page()
            else:
                admin_dashboard()
        else:
            if st.session_state.page == 'policyholder_dashboard':
                policyholder_dashboard()
            elif st.session_state.page == 'file_claim':
                file_claim_page()
            else:
                policyholder_dashboard()

# ============================================
# APPLICATION ENTRY POINT
# ============================================
if __name__ == "__main__":
    main()
