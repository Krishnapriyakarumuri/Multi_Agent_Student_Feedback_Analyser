# frontend/pages/1_Upload_Feedback.py - Upload & Process Feedback
import streamlit as st
import requests
import pandas as pd
import time

# Check auth
if "user_id" not in st.session_state or not st.session_state.user_id:
    st.switch_page("pages/0_Login.py")

# Only admins can upload
if st.session_state.get("role") != "admin":
    st.error("❌ Only admins can upload feedback. Contact your administrator.")
    st.stop()

st.set_page_config(page_title="Upload Feedback", page_icon="📤", layout="wide")

API_URL = "http://localhost:8000/api/v1"

st.markdown("<h2>📤 Upload Student Feedback</h2>", unsafe_allow_html=True)
st.markdown("Upload your feedback CSV file to begin analysis")

# Info section
with st.expander("📋 File Format & Requirements"):
    st.markdown("""
    **Required:**
    - File format: CSV
    - Must contain a column named `feedback_text`
    
    **Optional columns (for additional insights):**
    - `student_id` - Identifier for the student
    - `department` - Academic department
    - `semester` - Semester information
    - `year` - Academic year
    - `date` - Date of feedback
    
    **Example CSV:**
    ```
    feedback_text,department,semester
    "The course was well structured",Engineering,Spring2024
    "Need more practical examples",Business,Spring2024
    ```
    """)

# Upload section
st.markdown("---")
st.markdown("### 📁 Choose File")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], label_visibility="collapsed")

if uploaded_file is not None:
    # Preview uploaded data
    st.markdown("### 👀 Preview Data")
    
    try:
        df = pd.read_csv(uploaded_file)
        
        # Check for required columns
        if "feedback_text" not in df.columns:
            st.error("❌ CSV must contain a 'feedback_text' column")
            st.stop()
        
        # Display preview
        st.dataframe(df.head(10), use_container_width=True)
        
        st.markdown(f"**File Stats:** {len(df)} rows × {len(df.columns)} columns")
        
        # Display column names
        st.caption(f"Columns: {', '.join(df.columns.tolist())}")
        
        # Show data quality
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Valid Feedback", df["feedback_text"].notna().sum())
        with col3:
            st.metric("Missing Values", df["feedback_text"].isna().sum())
        
        st.markdown("---")
        
        # Upload button
        if st.button("🚀 Deploy Agents & Start Analysis", type="primary", use_container_width=True):
            with st.spinner("🔄 Orchestrator deploying agents..."):
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    files = {"file": uploaded_file}
                    response = requests.post(f"{API_URL}/feedback/upload", files=files, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        job_id = data.get("job_id")
                        
                        # Store job_id in session
                        st.session_state.job_id = job_id
                        st.session_state.total_feedbacks = data.get("total_feedbacks", 0)
                        
                        st.success(f"✅ Successfully deployed {len(data.get('agents_involved', []))} agents!")
                        st.markdown(f"**Job ID:** `{job_id}`")
                        st.markdown(f"**Total Feedback:** {data.get('total_feedbacks')} items")
                        st.markdown(f"**Agents:** {', '.join(data.get('agents_involved', []))}")
                        
                        st.markdown("---")
                        st.info("⏳ Pipeline is now running in the background. Go to Dashboard to monitor progress.")
                        
                        time.sleep(2)
                        st.switch_page("pages/2_Agent_Dashboard.py")
                    else:
                        st.error(f"❌ Upload failed: {response.text}")
                        
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timeout. Try with a smaller file or check the API server.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")

else:
    st.markdown("---")
    st.markdown("### 📚 Example Template")
    
    # Create a downloadable example CSV
    example_data = {
        "feedback_text": [
            "The course structure was excellent and well organized.",
            "More practical examples would be helpful.",
            "The instructor was not responsive to questions."
        ],
        "department": ["Engineering", "Business", "Science"],
        "semester": ["Spring 2024", "Spring 2024", "Fall 2023"]
    }
    
    example_df = pd.DataFrame(example_data)
    
    st.dataframe(example_df, use_container_width=True)
    
    csv = example_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Example Template",
        data=csv,
        file_name="feedback_template.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("✅ Your feedback will be analyzed by 6 specialized AI agents")