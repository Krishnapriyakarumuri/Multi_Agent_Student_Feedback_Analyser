# frontend/pages/3_Theme_Discovery.py
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Check auth
if "user_id" not in st.session_state or not st.session_state.user_id:
    st.switch_page("pages/0_Login.py")

st.set_page_config(page_title="Theme Discovery", page_icon="🔍", layout="wide")

API_URL = "http://localhost:8000/api/v1"

st.markdown("<h2>🔍 Theme Discovery Deep Dive</h2>", unsafe_allow_html=True)
st.markdown("Explore themes and patterns in student feedback")

try:
    resp = requests.get(f"{API_URL}/dashboard/charts", timeout=10)
    if resp.status_code != 200:
        st.info("⏳ No themes discovered yet. Upload feedback first.")
        st.stop()
    
    chart_data = resp.json()
    themes = list(chart_data.get("theme_sentiment", {}).keys())
    
    if not themes:
        st.info("⏳ Analyzing feedback for themes...")
        st.stop()
    
    # Theme selector
    selected_theme = st.selectbox("Select a theme to explore", themes)
    
    st.markdown("---")
    
    # Get data for selected theme
    theme_data = chart_data["theme_sentiment"][selected_theme]
    
    # Sentiment distribution for this theme
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 📌 {selected_theme}")
        st.markdown("**Sentiment Distribution:**")
        for sentiment, count in theme_data.items():
            st.markdown(f"  - {sentiment.capitalize()}: {count}")
    
    with col2:
        st.markdown("#### Sentiment Distribution")
        fig = go.Figure(data=[go.Pie(
            labels=list(theme_data.keys()),
            values=list(theme_data.values()),
            marker=dict(colors=["#10b981", "#6b7280", "#ef4444"])
        )])
        fig.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("#### 🏷️ Top Keywords")
    keywords = chart_data.get("top_keywords", [])[:10]
    if keywords:
        kw_df = pd.DataFrame(keywords)
        st.dataframe(kw_df, use_container_width=True)
    else:
        st.info("No keywords available")

except Exception as e:
    st.error(f"Error: {e}")