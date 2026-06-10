# frontend/components/agent_cards.py
import streamlit as st

def render_agent_card(name: str, role: str, status: str, tools: list):
    with st.container():
        emoji = "🟢" if status == "online" else "🔴"
        st.markdown(f"### {emoji} {name}")
        st.caption(f"Role: {role}")
        st.caption(f"Tools: {', '.join(tools)}")
        st.divider()