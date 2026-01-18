import streamlit as st

st.set_page_config(
    page_title="iRMC InsureAI ®",
    page_icon="🏥",
    layout="wide"
)

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
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">iRMC InsureAI ®</div>', unsafe_allow_html=True)
st.write("✅ App is loading...")

# Test basic functionality
if st.button("Test Button"):
    st.success("App is working!")
