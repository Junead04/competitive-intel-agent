"""pages/settings.py — API key configuration and preferences."""

import streamlit as st


def render_settings():
    st.markdown(
        """
        <div class="page-title">Settings</div>
        <div class="page-subtitle">Configure API keys, model preferences, and research defaults</div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["🔑 API Keys", "🤖 Model", "🔍 Research", "📊 Display"])

    with tabs[0]:
        _api_keys_tab()
    with tabs[1]:
        _model_tab()
    with tabs[2]:
        _research_tab()
    with tabs[3]:
        _display_tab()


# ── API Keys ──────────────────────────────────────────────────────────────────

def _api_keys_tab():
    st.markdown('<div class="section-title">🔑 API Keys</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="insight-block">API keys are stored in session memory only. '
        'For persistent storage, add them to <code>.streamlit/secrets.toml</code> '
        'or as environment variables. They are never sent anywhere except to the respective API providers.</div>',
        unsafe_allow_html=True,
    )

    # ── Groq ──────────────────────────────────────────────────────────────────
    st.markdown(
        """<div class="intel-card" style="margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">
                <div>
                    <span style="font-family:'Syne',sans-serif;font-weight:700;color:#f0f4ff;">Groq LLM</span>
                    <span class="badge badge-green" style="margin-left:0.5rem;">Required</span>
                </div>
                <a href="https://console.groq.com" target="_blank"
                   style="color:var(--accent-cyan);font-size:0.78rem;text-decoration:none;">
                   Get free key ↗</a>
            </div>
            <div style="color:var(--text-secondary);font-size:0.8rem;margin-bottom:0.5rem;">
                Powers the LLM analysis and synthesis. Free tier: 14,400 req/day.
                Recommended model: <code>llama3-70b-8192</code>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    groq_key = st.text_input(
        "Groq API Key",
        value=st.session_state.get("groq_api_key", ""),
        type="password",
        placeholder="gsk_...",
        key="groq_input",
    )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Tavily ────────────────────────────────────────────────────────────────
    st.markdown(
        """<div class="intel-card" style="margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">
                <div>
                    <span style="font-family:'Syne',sans-serif;font-weight:700;color:#f0f4ff;">Tavily Search</span>
                    <span class="badge badge-blue" style="margin-left:0.5rem;">Recommended</span>
                </div>
                <a href="https://tavily.com" target="_blank"
                   style="color:var(--accent-cyan);font-size:0.78rem;text-decoration:none;">
                   Get free key ↗</a>
            </div>
            <div style="color:var(--text-secondary);font-size:0.8rem;margin-bottom:0.5rem;">
                Primary web search. Optimized for LLM agents. Free tier: 1,000 searches/month.
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    tavily_key = st.text_input(
        "Tavily API Key",
        value=st.session_state.get("tavily_api_key", ""),
        type="password",
        placeholder="tvly-...",
        key="tavily_input",
    )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── SerpAPI ───────────────────────────────────────────────────────────────
    st.markdown(
        """<div class="intel-card" style="margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">
                <div>
                    <span style="font-family:'Syne',sans-serif;font-weight:700;color:#f0f4ff;">SerpAPI</span>
                    <span class="badge badge-violet" style="margin-left:0.5rem;">Optional</span>
                </div>
                <a href="https://serpapi.com" target="_blank"
                   style="color:var(--accent-cyan);font-size:0.78rem;text-decoration:none;">
                   Get free key ↗</a>
            </div>
            <div style="color:var(--text-secondary);font-size:0.8rem;margin-bottom:0.5rem;">
                Google search fallback. Free tier: 100 searches/month. Used when Tavily is unavailable.
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    serpapi_key = st.text_input(
        "SerpAPI Key",
        value=st.session_state.get("serpapi_key", ""),
        type="password",
        placeholder="your-serpapi-key",
        key="serp_input",
    )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if st.button("💾  Save API Keys", use_container_width=False):
        st.session_state.groq_api_key   = groq_key.strip()
        st.session_state.tavily_api_key = tavily_key.strip()
        st.session_state.serpapi_key    = serpapi_key.strip()
        st.success("✅ API keys saved to session!")

    # Test connection
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("🔌  Test Groq Connection", use_container_width=False):
        _test_groq(st.session_state.get("groq_api_key", ""))


def _test_groq(key: str):
    if not key:
        st.error("No Groq key set.")
        return
    with st.spinner("Testing connection..."):
        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(api_key=key, model_name="llama3-8b-8192", max_tokens=20)
            llm.invoke("Say 'OK' and nothing else.")
            st.success("✅ Groq connection successful!")
        except Exception as e:
            st.error(f"❌ Connection failed: {e}")


# ── Model Settings ────────────────────────────────────────────────────────────

def _model_tab():
    st.markdown('<div class="section-title">🤖 LLM Configuration</div>', unsafe_allow_html=True)

    models = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "gemma2-9b-it",
    ]

    # ✅ NEW
    model_desc = {
        "llama-3.3-70b-versatile": "Best quality — Llama 3.3 70B. Official replacement for llama3-70b. Recommended.",
        "llama-3.1-8b-instant":    "Fastest & cheapest — 8B model. Good for quick research or testing.",
        "llama-3.1-70b-versatile": "Alternative 70B — slightly older than 3.3 but still very capable.",
        "gemma2-9b-it":            "Google Gemma 2 — lightweight, instruction-tuned, good for simple tasks.",
    }

    current_model = st.session_state.get("llm_model", "llama-3.3-70b-versatile")
    model = st.selectbox(
        "Groq Model",
        models,
        index=models.index(current_model) if current_model in models else 0,
    )

    st.markdown(
        f'<div class="insight-block">{model_desc.get(model, "")}</div>',
        unsafe_allow_html=True,
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.get("temperature", 0.3),
        step=0.05,
        help="Lower = more factual & deterministic. Higher = more creative.",
    )

    st.markdown(
        f'<div class="insight-block">Temperature <strong>{temperature}</strong> — '
        f'{"Factual / deterministic" if temperature < 0.3 else "Balanced" if temperature < 0.6 else "Creative / exploratory"}'
        f'</div>',
        unsafe_allow_html=True,
    )

    if st.button("💾  Save Model Settings"):
        st.session_state.llm_model   = model
        st.session_state.temperature = temperature
        st.success("✅ Model settings saved!")


# ── Research Defaults ─────────────────────────────────────────────────────────

def _research_tab():
    st.markdown('<div class="section-title">🔍 Research Defaults</div>', unsafe_allow_html=True)

    depth = st.selectbox(
        "Default Research Depth",
        ["quick", "standard", "comprehensive"],
        index=["quick", "standard", "comprehensive"].index(
            st.session_state.get("report_depth", "standard")
        ),
    )

    max_results = st.slider(
        "Max Search Results per Query",
        min_value=3,
        max_value=10,
        value=st.session_state.get("max_search_results", 5),
    )

    auto_save = st.toggle(
        "Auto-save reports",
        value=st.session_state.get("auto_save_reports", True),
    )

    provider = st.radio(
        "Preferred Search Provider",
        ["tavily", "serpapi"],
        index=0 if st.session_state.get("search_provider", "tavily") == "tavily" else 1,
        horizontal=True,
    )

    if st.button("💾  Save Research Settings"):
        st.session_state.report_depth      = depth
        st.session_state.max_search_results = max_results
        st.session_state.auto_save_reports  = auto_save
        st.session_state.search_provider    = provider
        st.success("✅ Research settings saved!")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🗑️ Danger Zone</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="insight-block danger">Clearing reports will permanently remove all saved research from this session.</div>',
        unsafe_allow_html=True,
    )
    if st.button("🗑️ Clear All Reports", type="secondary"):
        st.session_state.reports             = []
        st.session_state.tracked_competitors = []
        st.session_state.search_count        = 0
        st.session_state.current_research    = None
        st.session_state.agent_logs          = []
        st.success("All reports cleared.")
        st.rerun()


# ── Display Settings ──────────────────────────────────────────────────────────

def _display_tab():
    st.markdown('<div class="section-title">📊 Display Preferences</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="insight-block">Display settings are cosmetic and affect how reports are rendered. '
        'They do not affect the research process.</div>',
        unsafe_allow_html=True,
    )

    st.toggle("Show agent logs during research", value=True, disabled=True)
    st.toggle("Auto-scroll to results after research", value=True, disabled=True)
    st.toggle("Compact competitor cards", value=False, disabled=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # System info
    st.markdown('<div class="section-title">ℹ️ System Info</div>', unsafe_allow_html=True)
    import sys, streamlit
    st.markdown(
        f"""<div class="intel-card">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;font-size:0.82rem;">
                <div style="color:var(--text-secondary);">Platform</div>
                <div style="color:var(--text-primary);">CompeteIQ v1.0.0</div>
                <div style="color:var(--text-secondary);">Streamlit</div>
                <div style="color:var(--text-primary);">{streamlit.__version__}</div>
                <div style="color:var(--text-secondary);">Python</div>
                <div style="color:var(--text-primary);">{sys.version[:10]}</div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
