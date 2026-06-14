import streamlit as st
import requests
import plotly.graph_objects as go

# Check auth
if "user_id" not in st.session_state or not st.session_state.user_id:
    st.switch_page("pages/0_Login.py")

st.set_page_config(page_title="Sentiment Analysis", page_icon="😊", layout="wide")

API_URL = "http://localhost:8000/api/v1"

st.markdown("<h2>😊 Sentiment Analysis</h2>", unsafe_allow_html=True)
st.markdown("Overall sentiment breakdown across all feedback")

try:
    resp = requests.get(f"{API_URL}/dashboard/summary", timeout=10)
    if resp.status_code != 200:
        st.info("⏳ No sentiment data yet. Upload feedback first.")
        st.stop()
    
    summary = resp.json()
    
    st.markdown("---")
    
    # Overall sentiment
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("😊 Positive", f"{summary['sentiment']['positive_pct']}%", delta=summary['sentiment']['positive'])
    
    with col2:
        st.metric("😐 Neutral", f"{summary['sentiment']['neutral_pct']}%", delta=summary['sentiment']['neutral'])
    
    with col3:
        st.metric("😞 Negative", f"{summary['sentiment']['negative_pct']}%", delta=summary['sentiment']['negative'])
    
    st.markdown("---")
    
    # Sentiment donut chart
    st.markdown("#### Overall Distribution")
    
    fig = go.Figure(data=[go.Pie(
        labels=['Positive', 'Neutral', 'Negative'],
        values=[summary['sentiment']['positive'], summary['sentiment']['neutral'], summary['sentiment']['negative']],
        marker=dict(colors=['#10b981', '#6b7280', '#ef4444']),
        hole=.3
    )])
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.info("💡 Sentiment analysis is automatically performed as part of the feedback analysis pipeline.")

except Exception as e:
    st.error(f"Error: {e}")