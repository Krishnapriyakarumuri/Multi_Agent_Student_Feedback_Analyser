# frontend/app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Multi-Agent Feedback Analyzer", page_icon="🤖", layout="wide")

API_URL = "http://localhost:8000/api/v1"

st.title("🤖 Multi-Agent Student Feedback Intelligence Platform")
st.markdown("### AI Agents working together to analyze institutional feedback")

# Sidebar
with st.sidebar:
    st.header("📤 Upload Feedback")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    
    if uploaded_file and st.button("🚀 Deploy Agents", type="primary"):
        with st.spinner("Orchestrator deploying agents..."):
            files = {"file": uploaded_file}
            response = requests.post(f"{API_URL}/feedback/upload", files=files)
            if response.status_code == 200:
                data = response.json()
                st.session_state.job_id = data["job_id"]
                st.success(f"✅ {len(data['agents_involved'])} agents deployed!")
    
    st.divider()
    st.header("🤖 Agent Status")
    if st.button("Refresh Agent Status"):
        response = requests.get(f"{API_URL}/agents/status")
        if response.status_code == 200:
            agents = response.json()
            for agent in agents.get("agent_details", []):
                emoji = "🟢" if agent["status"] == "online" else "🔴"
                st.text(f"{emoji} {agent['name']}")

# Main content
col1, col2, col3, col4 = st.columns(4)
col1.metric("Agents Online", "6", "All active")
col2.metric("Tasks Completed", "245", "+18%")
col3.metric("Themes Discovered", "12", "Dynamic")
col4.metric("Bias Flags", "3", "Under review")

# Job progress
if "job_id" in st.session_state:
    st.divider()
    st.header("🔄 Agent Processing Pipeline")
    
    job_id = st.session_state.job_id
    
    # Initialize session state for polling
    if "polling_active" not in st.session_state:
        st.session_state.polling_active = True
        st.session_state.poll_count = 0
    
    # Create placeholders for real-time updates
    progress_container = st.container()
    queue_container = st.container()
    worker_status_container = st.container()
    debug_container = st.container()
    
    # Poll once per rerun
    if st.session_state.polling_active:
        st.session_state.poll_count += 1
        
        try:
            response = requests.get(f"{API_URL}/jobs/{job_id}/detailed-status", timeout=3)
            if response.status_code == 200:
                status = response.json()
                
                with progress_container:
                    col1, col2 = st.columns(2)
                    with col1:
                        progress_percent = status.get("progress_percent", 0)
                        st.progress(min(progress_percent / 100, 1.0))
                        st.text(f"Progress: {progress_percent:.1f}%")
                    
                    with col2:
                        st.metric("Status", status["status"])
                
                with queue_container:
                    st.subheader("📊 Agent Queue Status")
                    
                    agents = status.get("agents_involved", [])
                    queue_status = status.get("queue_status", {})
                    
                    # Create queue visualization
                    queue_data = []
                    for agent in agents:
                        depth = queue_status.get(agent, 0)
                        is_completed = agent in status.get("completed_agents", [])
                        queue_data.append({
                            "Agent": agent,
                            "Tasks in Queue": depth,
                            "Status": "✅ Complete" if is_completed else "⏳ Processing" if depth > 0 else "⏹️ Idle"
                        })
                    
                    df_queues = pd.DataFrame(queue_data)
                    st.dataframe(df_queues, width='stretch', hide_index=True)
                
                with worker_status_container:
                    current_agent = status.get('current_agent', 'unknown')
                    completed = ', '.join(status['completed_agents']) if status['completed_agents'] else 'None'
                    st.caption(f"Current: {current_agent} | Completed: {completed}")
                
                if status["status"] == "completed":
                    st.success("✅ Pipeline Complete! All agents finished processing.")
                    st.balloons()
                    st.session_state.polling_active = False
                else:
                    # Trigger rerun after 2 seconds
                    import time
                    time.sleep(2)
                    st.rerun()
            else:
                with debug_container:
                    st.warning(f"⚠️ API returned status {response.status_code}")
                st.session_state.polling_active = False
        
        except requests.exceptions.Timeout:
            with debug_container:
                st.warning("⚠️ Request timed out (server might be slow)")
            import time
            time.sleep(3)
            st.rerun()
        
        except requests.exceptions.ConnectionError:
            with debug_container:
                st.error("❌ Cannot connect to server. Is it running on port 8000?")
            st.session_state.polling_active = False
        
        except Exception as e:
            with debug_container:
                st.warning(f"⚠️ Error: {str(e)}")
            st.session_state.polling_active = False

st.divider()
st.caption(f"Multi-Agent System v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")