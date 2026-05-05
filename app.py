import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="CompeteIQ — Competitive Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/yourusername/competitive-intel-agent",
        "Report a bug": "https://github.com/yourusername/competitive-intel-agent/issues",
        "About": "# CompeteIQ\nAI-driven competitive intelligence platform powered by LangChain agents.",
    },
)

from components.styles import inject_styles
from components.sidebar import render_sidebar
from pages.dashboard import render_dashboard
from pages.research import render_research
from pages.reports import render_reports
from pages.settings import render_settings
from utils.session import init_session_state

# Initialize session state
init_session_state()

# Inject global CSS
inject_styles()

# Render sidebar and get current page
current_page = render_sidebar()

# Route to correct page
if current_page == "Dashboard":
    render_dashboard()
elif current_page == "Research":
    render_research()
elif current_page == "Reports":
    render_reports()
elif current_page == "Settings":
    render_settings()
