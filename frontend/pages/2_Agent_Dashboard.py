# frontend/pages/2_Agent_Dashboard.py
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Check auth
if "user_id" not in st.session_state or not st.session_state.user_id:
    st.switch_page("pages/0_Login.py")

st.set_page_config(page_title="Dashboard Overview", page_icon="📊", layout="wide")

API_URL = "http://localhost:8000/api/v1"

st.markdown("<h2>📊 Dashboard Overview</h2>", unsafe_allow_html=True)

# Fetch dashboard data
try:
    summary_resp = requests.get(f"{API_URL}/dashboard/summary", timeout=10)
    chart_resp = requests.get(f"{API_URL}/dashboard/charts", timeout=10)
    
    if summary_resp.status_code != 200 or chart_resp.status_code != 200:
        st.warning("⚠️ No data yet. Please upload feedback to see insights.")
        st.stop()
    
    summary = summary_resp.json()
    chart_data = chart_resp.json()
except Exception as e:
    st.error(f"❌ Error loading dashboard: {e}")
    st.stop()

# KPI Row 1
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Feedbacks", summary["total_feedbacks"], delta="Live")

with col2:
    st.metric("Positive Sentiment", f"{summary['sentiment']['positive_pct']}%", 
              delta=f"{summary['sentiment']['positive']} responses")

with col3:
    st.metric("Neutral Sentiment", f"{summary['sentiment']['neutral_pct']}%", 
              delta=f"{summary['sentiment']['neutral']} responses")

with col4:
    st.metric("Negative Sentiment", f"{summary['sentiment']['negative_pct']}%", 
              delta=f"{summary['sentiment']['negative']} responses")

st.markdown("---")

# KPI Row 2 - Recommendations & Issues
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🔴 High Priority", summary["recommendations"]["high_priority"])

with col2:
    st.metric("🟡 Medium Priority", summary["recommendations"]["medium_priority"])

with col3:
    st.metric("🟢 Low Priority", summary["recommendations"]["low_priority"])

with col4:
    st.metric("⚠️ Bias Issues", summary["bias_issues"])

st.markdown("---")

# Charts Section
st.markdown("### 📈 Insights & Analytics")

chart_col1, chart_col2 = st.columns(2)

# Sentiment Donut Chart
with chart_col1:
    st.markdown("#### Overall Sentiment Distribution")
    sentiment_data = {
        "Positive": summary["sentiment"]["positive"],
        "Neutral": summary["sentiment"]["neutral"],
        "Negative": summary["sentiment"]["negative"]
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=list(sentiment_data.keys()),
        values=list(sentiment_data.values()),
        marker=dict(colors=["#10b981", "#6b7280", "#ef4444"]),
        hole=.3
    )])
    fig.update_layout(
        template="plotly_dark",
        showlegend=True,
        height=400,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# Recommendations Priority Chart
with chart_col2:
    st.markdown("#### Unresolved Recommendations by Priority")
    priority_data = {
        "High": summary["recommendations"]["high_priority"],
        "Medium": summary["recommendations"]["medium_priority"],
        "Low": summary["recommendations"]["low_priority"]
    }
    
    fig = go.Figure(data=[go.Bar(
        x=list(priority_data.keys()),
        y=list(priority_data.values()),
        marker=dict(color=["#ef4444", "#f59e0b", "#10b981"])
    )])
    fig.update_layout(
        template="plotly_dark",
        title="",
        xaxis_title="Priority Level",
        yaxis_title="Count",
        height=400,
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Theme x Sentiment Analysis
st.markdown("#### 📌 Feedback by Theme & Sentiment")

if chart_data.get("theme_sentiment"):
    theme_df = []
    for theme, sentiment_counts in chart_data["theme_sentiment"].items():
        for sentiment, count in sentiment_counts.items():
            theme_df.append({"Theme": theme, "Sentiment": sentiment, "Count": count})
    
    theme_df = pd.DataFrame(theme_df)
    
    fig = px.bar(
        theme_df,
        x="Theme",
        y="Count",
        color="Sentiment",
        barmode="group",
        color_discrete_map={"positive": "#10b981", "neutral": "#6b7280", "negative": "#ef4444"}
    )
    fig.update_layout(
        template="plotly_dark",
        height=400,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No theme data available yet.")

st.markdown("---")

# Top Keywords
st.markdown("#### 🏷️ Top Keywords Across Feedback")

if chart_data.get("top_keywords"):
    keywords = chart_data["top_keywords"]
    keywords_df = pd.DataFrame(keywords)
    
    fig = px.bar(
        keywords_df,
        x="keyword",
        y="count",
        title="",
        labels={"keyword": "Keyword", "count": "Frequency"},
        color="count",
        color_continuous_scale="Purples"
    )
    fig.update_layout(
        template="plotly_dark",
        height=400,
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No keyword data available yet.")

st.markdown("---")

# Status info
st.caption(f"🔄 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")