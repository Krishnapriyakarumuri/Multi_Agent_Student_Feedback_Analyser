# frontend/app.py - Main Navigation & Auth Guard
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="Student Feedback Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global API URL
API_URL = "http://localhost:8000/api/v1"

# Auth Guard: Redirect to login if not authenticated
def check_authentication():
    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.switch_page("pages/0_Login.py")

check_authentication()

# Global Styling
st.markdown("""
    <style>
    :root {
        --bg-primary: #0f1117;
        --bg-secondary: #1a1f2e;
        --accent: #7c3aed;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    /* Dark mode background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f1117 0%, #1a1f2e 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(26, 31, 46, 0.8);
        border-right: 1px solid rgba(124, 58, 237, 0.1);
    }
    
    /* Card styling */
    .metric-card {
        background: rgba(26, 31, 46, 0.6);
        border: 1px solid rgba(124, 58, 237, 0.2);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(10px);
    }
    
    /* Priority badges */
    .priority-high {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        color: #fca5a5;
    }
    .priority-medium {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        color: #fcd34d;
    }
    .priority-low {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        color: #86efac;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.markdown("---")
    
    # User Info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**👤 {st.session_state.get('username', 'User')}**")
        role_badge = "👑 Admin" if st.session_state.get("role") == "admin" else "👁️ Viewer"
        st.markdown(f"<small>{role_badge}</small>", unsafe_allow_html=True)
    
    with col2:
        if st.button("🚪", help="Logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.role = None
            st.switch_page("pages/0_Login.py")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📋 Navigation")
    pages = {
        "📤 Upload Feedback": "pages/1_Upload_Feedback.py",
        "📊 Dashboard": "pages/2_Agent_Dashboard.py",
        "💡 Themes": "pages/3_Theme_Discovery.py",
        "😊 Sentiment": "pages/4_Sentiment_Analysis.py",
        "⚖️ Bias Report": "pages/5_Bias_Report.py",
        "✨ Recommendations": "pages/6_Recommendations.py",
    }
    
    for page_name, page_file in pages.items():
        if st.button(page_name, use_container_width=True):
            st.switch_page(page_file)
    
    st.markdown("---")

# Main Page
st.markdown("<h1 style='text-align: center;'>🤖 Multi-Agent Student Feedback Intelligence Platform</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>AI Agents working together to analyze institutional feedback</h3>", unsafe_allow_html=True)

# Welcome message
st.info(f"✅ Logged in as **{st.session_state.get('username')}** ({st.session_state.get('role')})")

# Quick start guide
st.markdown("""
### 🚀 Quick Start Guide

1. **Upload Feedback** - Go to the Upload page and upload your CSV with student feedback
2. **View Dashboard** - Monitor KPIs, sentiment trends, and top themes
3. **Review Recommendations** - See AI-generated recommendations with priority levels
4. **Manage Issues** - Admins can mark recommendations as resolved

#### 📊 Dashboard Features
- **KPI Cards**: Total feedback, sentiment breakdown, critical issues
- **Charts**: Theme distribution, sentiment trends, keyword analysis
- **Top Recommendations**: Prioritized action items to improve the institution

#### ✨ Recommendation System
- **Priority Levels**: High 🔴 | Medium 🟡 | Low 🟢
- **Action Items**: Specific steps to implement recommendations
- **Admin Controls**: Mark recommendations as resolved (admin only)
""")

# Footer
st.markdown("---")
st.caption(f"🛡️ Multi-Agent Student Feedback Intelligence Platform | v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")