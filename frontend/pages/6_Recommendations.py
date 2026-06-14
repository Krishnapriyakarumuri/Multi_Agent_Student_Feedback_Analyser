# frontend/pages/6_Recommendations.py - AI-Generated Recommendations
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Check auth
if "user_id" not in st.session_state or not st.session_state.user_id:
    st.switch_page("pages/0_Login.py")

st.set_page_config(page_title="Recommendations", page_icon="✨", layout="wide")

API_URL = "http://localhost:8000/api/v1"
is_admin = st.session_state.get("role") == "admin"

st.markdown("<h2>✨ AI-Generated Recommendations</h2>", unsafe_allow_html=True)
st.markdown("Actionable recommendations based on feedback analysis")

# Fetch recommendations
try:
    resp = requests.get(f"{API_URL}/recommendations/with-meta", timeout=10)
    
    if resp.status_code != 200:
        st.error(f"❌ Error loading recommendations: HTTP {resp.status_code}")
        st.stop()
    
    data = resp.json()
    recommendations = data.get("recommendations", [])
    
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.stop()

# Empty state
if not recommendations:
    st.info("📭 No active recommendations. All recommendations have been resolved!")
    st.markdown("---")
    st.markdown("#### 📊 How to get started:")
    st.markdown("""
    1. Go to **Upload Feedback** to upload student feedback CSV
    2. Wait for the pipeline to complete
    3. Recommendations will appear here with priority levels and action items
    """)
    st.stop()

# Filter controls
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    priority_filter = st.selectbox(
        "Filter by Priority",
        ["All", "High 🔴", "Medium 🟡", "Low 🟢"],
        key="priority_filter"
    )

with col2:
    theme_filter = st.selectbox(
        "Filter by Theme",
        ["All"] + list(set(r["theme_name"] for r in recommendations)),
        key="theme_filter"
    )

# Apply filters
filtered_recs = recommendations
if priority_filter != "All":
    priority_map = {"High 🔴": "high", "Medium 🟡": "medium", "Low 🟢": "low"}
    filtered_recs = [r for r in filtered_recs if r["priority"] == priority_map[priority_filter]]

if theme_filter != "All":
    filtered_recs = [r for r in filtered_recs if r["theme_name"] == theme_filter]

st.markdown(f"### Found {len(filtered_recs)} recommendation(s)")
st.markdown("---")

# Priority color mapping
priority_colors = {
    "high": "#ef4444",
    "medium": "#f59e0b",
    "low": "#10b981"
}

priority_icons = {
    "high": "🔴",
    "medium": "🟡",
    "low": "🟢"
}

# Display recommendations as cards
for i, rec in enumerate(filtered_recs):
    with st.container(border=True):
        # Header with theme and priority
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"#### 📌 {rec['theme_name']}")
        
        with col2:
            priority_badge = f"{priority_icons[rec['priority']]} {rec['priority'].upper()}"
            st.markdown(f"<div style='background: rgba({priority_colors[rec['priority']]}, 0.1); padding: 8px; border-radius: 6px; text-align: center;'><strong>{priority_badge}</strong></div>", unsafe_allow_html=True)
        
        with col3:
            st.caption(f"📅 {rec['created_at'][:10]}")
        
        st.markdown("---")
        
        # Recommendation text
        st.markdown(f"**Recommendation:** {rec['recommendation_text']}")
        
        # Expected impact
        if rec.get('expected_impact'):
            st.markdown(f"**Expected Impact:** {rec['expected_impact']}")
        
        # Action items
        if rec.get('action_items'):
            st.markdown("**Action Items:**")
            for idx, action in enumerate(rec['action_items'], 1):
                st.markdown(f"  {idx}. {action}")
        
        # Fairness note
        if rec.get('fairness_note'):
            st.info(f"⚖️ **Fairness Note:** {rec['fairness_note']}")
        
        # Feedback preview
        if rec.get('feedback_preview'):
            st.markdown(f"**📄 Original Feedback:** _{rec['feedback_preview']}_")
        
        # Admin actions
        if is_admin:
            st.markdown("---")
            admin_col1, admin_col2 = st.columns([1, 3])
            
            with admin_col1:
                if st.button(f"✅ Mark Resolved", key=f"resolve_{rec['id']}", help="Mark this recommendation as implemented"):
                    try:
                        resolve_resp = requests.patch(f"{API_URL}/recommendations/{rec['id']}/resolve", timeout=10)
                        if resolve_resp.status_code == 200:
                            st.success("✅ Recommendation marked as resolved!")
                            st.rerun()
                        else:
                            st.error(f"Error: {resolve_resp.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with admin_col2:
                st.caption("👑 Admin only: Mark this recommendation as implemented and remove from active view")
        else:
            st.markdown("---")
            st.caption("👁️ Viewer mode: Contact admin to resolve recommendations")
        
        st.markdown("")

# Summary statistics
st.markdown("---")
st.markdown("### 📊 Recommendation Summary")

summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

total_high = sum(1 for r in recommendations if r["priority"] == "high")
total_medium = sum(1 for r in recommendations if r["priority"] == "medium")
total_low = sum(1 for r in recommendations if r["priority"] == "low")
total = len(recommendations)

with summary_col1:
    st.metric("🔴 High Priority", total_high)

with summary_col2:
    st.metric("🟡 Medium Priority", total_medium)

with summary_col3:
    st.metric("🟢 Low Priority", total_low)

with summary_col4:
    st.metric("📋 Total Active", total)

st.markdown("---")
st.caption(f"🔄 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")