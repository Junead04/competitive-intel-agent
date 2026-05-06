import streamlit as st
import os


def init_session_state():
    """Initialize all session state variables with sensible defaults."""

    defaults = {
        # Navigation
        "current_page": "Dashboard",

        # API keys — load from env or Streamlit secrets if available
        "groq_api_key":   _safe_secret("GROQ_API_KEY"),
        "tavily_api_key": _safe_secret("TAVILY_API_KEY"),
        "serpapi_key":    _safe_secret("SERPAPI_KEY"),

        # Research session
        "current_research": None,
        "research_running": False,
        "agent_logs": [],
        "search_count": 0,

        # Data stores
        "reports": [],
        "tracked_competitors": [],

        # Settings
        "llm_model": "llama-3.1-8b-instant",
        "max_search_results": 5,
        "report_depth": "comprehensive",
        "auto_save_reports": True,
        "search_provider": "tavily",
        "temperature": 0.3,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _safe_secret(key: str) -> str:
    """Try Streamlit secrets first, then env vars, else empty string."""
    try:
        return st.secrets.get(key, os.environ.get(key, ""))
    except Exception:
        return os.environ.get(key, "")
