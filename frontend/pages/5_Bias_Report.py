# frontend/pages/5_Bias_Report.py
import streamlit as st
import requests
import pandas as pd

# Check auth
if "user_id" not in st.session_state or not st.session_state.user_id:
    st.switch_page("pages/0_Login.py")

st.set_page_config(page_title="Bias Report", page_icon="⚖️", layout="wide")

API_URL = "http://localhost:8000/api/v1"

st.markdown("<h2>⚖️ Bias Detection Report</h2>", unsafe_allow_html=True)
st.markdown("Monitor bias and fairness issues in feedback")

try:
    summary_resp = requests.get(f"{API_URL}/dashboard/summary", timeout=10)
    bias_resp = requests.get(f"{API_URL}/bias/report", timeout=10)
    
    if summary_resp.status_code != 200:
        st.info("⏳ No bias data yet. Upload feedback first.")
        st.stop()
    
    summary = summary_resp.json()
    bias_data = bias_resp.json() if bias_resp.status_code == 200 else {}
    
    # KPIs
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("⚠️ Flagged for Bias", summary['bias_issues'])
    
    with col2:
        st.metric("✅ Clean Feedback", summary['total_feedbacks'] - summary['bias_issues'])
    
    st.markdown("---")
    
    # Bias details
    if bias_data.get('details'):
        st.markdown("#### Bias Type Breakdown")
        bias_df = pd.DataFrame(bias_data['details'])
        st.dataframe(bias_df, use_container_width=True)
    else:
        st.info("✅ No bias issues detected in the current dataset.")
    
    st.markdown("---")
    st.warning("⚠️ All flagged items are reviewed by the system for educational value before recommendations are generated. Admin review may be needed for sensitive cases.")

except Exception as e:
    st.error(f"Error: {e}")