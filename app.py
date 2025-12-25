import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="SurakshaNet Defense Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_URL = "http://localhost:8000"

# Styling
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #41424b;
    }
    .high-risk { color: #ff4b4b; }
    .medium-risk { color: #ffa726; }
    .low-risk { color: #00c853; }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🛡️ SurakshaNet")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["Dashboard", "Threat Analysis", "System Health"])
st.sidebar.markdown("---")
st.sidebar.info(f"Connected to: {BASE_URL}")

def get_status_color(score):
    if score < 30: return "low-risk"
    if score < 70: return "medium-risk"
    return "high-risk"

if page == "Dashboard":
    st.title("security Overview")
    
    # Fetch Stats
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/admin/stats")
        if resp.status_code == 200:
            stats = resp.json()
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Scans", stats.get("total_analyses", 0))
            with c2:
                st.metric("Threats Detected", stats.get("threats_detected", 0))
            with c3:
                st.metric("System Uptime", stats.get("uptime", "N/A"))
        else:
            st.error("Failed to fetch stats.")
    except Exception as e:
        st.error(f"Connection Error: {e}")

    st.markdown("### Recent Alerts")
    st.info("No recent alerts in this demo view.")

elif page == "Threat Analysis":
    st.title("🕵️ Threat Analysis Lab")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Content Input")
        sender = st.text_input("Sender Address", placeholder="e.g. ceo@fake-company.com")
        subject = st.text_input("Subject", placeholder="e.g. Urgent Wire Transfer")
        content_type = st.selectbox("Content Type", ["Text/Email", "Image", "Video (Coming Soon)"])
        
        content = ""
        if content_type == "Text/Email":
            content = st.text_area("Message Body", height=200, placeholder="Paste email or message content here...")
        
        analyze_btn = st.button("Analyze Content", type="primary", use_container_width=True)

    if analyze_btn:
        with st.spinner("Running Multi-Agent Analysis..."):
            try:
                # Prepare Payload
                payload = {
                    "content_type": "email",
                    "sender": sender or "unknown",
                    "subject": subject or "no subject",
                    "text_content": content,
                    "auto_respond": "true"
                }
                
                # Make Request
                response = requests.post(f"{BASE_URL}/api/v1/analyze/complete", data=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display Results
                    st.divider()
                    st.subheader("Analysis Results")
                    
                    # Top Level Metrics
                    r1, r2, r3 = st.columns(3)
                    score = result.get('threat_score', 0)
                    category = result.get('threat_category', 'UNKNOWN')
                    
                    r1.metric("Threat Score", f"{score:.1f}/100")
                    r2.metric("Category", category, delta_color="inverse")
                    r3.metric("Type", result.get('threat_type', 'Unknown'))
                    
                    # Visual Gauge (Simple bar)
                    st.progress(min(score / 100.0, 1.0))
                    
                    # Details
                    c_left, c_right = st.columns(2)
                    
                    with c_left:
                        st.markdown("### 🔍 Detailed Report")
                        st.text(result.get("detailed_report", ""))
                        
                    with c_right:
                        st.markdown("### 🛡️ Defense Actions")
                        actions = result.get("actions_taken", [])
                        if actions:
                            for action in actions:
                                st.warning(f"ACTION EXECUTED: {action}")
                        else:
                            st.success("No defensive actions required.")
                            
                        st.markdown("### 🚩 Indicators")
                        # We don't have raw indicators in the top level response often, 
                        # but check detailed report text or if we added them to response model.
                        # For now, just show summary.
                        st.info(result.get("summary", ""))

                    with st.expander("View Raw JSON Response"):
                        st.json(result)
                        
                else:
                    st.error(f"Analysis failed: {response.status_code}")
                    st.text(response.text)
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif page == "System Health":
    st.title("System Health")
    if st.button("Check Connectivity"):
        try:
            r = requests.get(f"{BASE_URL}/health")
            st.success(f"Status: {r.status_code}")
            st.json(r.json())
        except Exception as e:
            st.error(f"Failed to connect: {e}")
