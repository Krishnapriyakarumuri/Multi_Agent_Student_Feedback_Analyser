# frontend/components/charts.py
import plotly.express as px
import pandas as pd

def create_sentiment_chart(data: dict):
    df = pd.DataFrame({"Sentiment": ["Positive", "Negative", "Neutral"], "Count": [data.get("positive", 0), data.get("negative", 0), data.get("neutral", 0)]})
    return px.pie(df, values="Count", names="Sentiment", title="Sentiment Distribution")