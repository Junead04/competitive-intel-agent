import streamlit as st


NAV_ITEMS = [
    ("Dashboard", "⚡", "Overview & live metrics"),
    ("Research",  "🔍", "Run competitive research"),
    ("Reports",   "📊", "Saved intelligence reports"),
    ("Settings",  "⚙️",  "API keys & preferences"),
]


def render_sidebar() -> str:
    with st.sidebar:
        # ── Logo ──────────────────────────────────────
        st.markdown(
            """
            <div style="padding: 1.4rem 1rem 1rem; border-bottom: 1px solid rgba(99,179,237,0.12); margin-bottom: 1rem;">
                <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.2rem;">
                    <div style="width:32px;height:32px;background:linear-gradient(135deg,#38bdf8,#8b5cf6);
                                border-radius:8px;display:flex;align-items:center;justify-content:center;
                                font-size:1rem;">⚡</div>
                    <span style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:800;
                                 color:#f0f4ff;letter-spacing:-0.02em;">CompeteIQ</span>
                </div>
                <p style="color:#4b5563;font-size:0.7rem;margin:0;padding-left:2.5rem;
                           letter-spacing:0.08em;text-transform:uppercase;font-weight:500;">
                    Intelligence Platform
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Navigation ────────────────────────────────
        st.markdown(
            "<p style='color:#4b5563;font-size:0.68rem;font-weight:600;letter-spacing:0.1em;"
            "text-transform:uppercase;padding:0 1rem;margin-bottom:0.4rem;'>Navigation</p>",
            unsafe_allow_html=True,
        )

        if "current_page" not in st.session_state:
            st.session_state.current_page = "Dashboard"

        for label, icon, tooltip in NAV_ITEMS:
            is_active = st.session_state.current_page == label
            active_class = "active" if is_active else ""
            st.markdown(
                f"""<div class="nav-item {active_class}" title="{tooltip}">
                        <span class="nav-icon">{icon}</span>
                        <span>{label}</span>
                    </div>""",
                unsafe_allow_html=True,
            )
            # Invisible button over the styled div
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                st.session_state.current_page = label
                st.rerun()

        st.markdown("<hr style='margin:1rem 0;'>", unsafe_allow_html=True)

        # ── Quick Stats ───────────────────────────────
        st.markdown(
            "<p style='color:#4b5563;font-size:0.68rem;font-weight:600;letter-spacing:0.1em;"
            "text-transform:uppercase;padding:0 1rem;margin-bottom:0.8rem;'>Session Stats</p>",
            unsafe_allow_html=True,
        )

        reports_count = len(st.session_state.get("reports", []))
        searches_count = st.session_state.get("search_count", 0)
        competitors_tracked = len(st.session_state.get("tracked_competitors", []))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""<div style="background:#111827;border:1px solid rgba(99,179,237,0.12);
                    border-radius:10px;padding:0.8rem;text-align:center;margin-bottom:0.5rem;">
                    <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
                         background:linear-gradient(135deg,#38bdf8,#8b5cf6);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;">{reports_count}</div>
                    <div style="color:#4b5563;font-size:0.62rem;font-weight:600;
                         letter-spacing:0.08em;text-transform:uppercase;margin-top:2px;">Reports</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""<div style="background:#111827;border:1px solid rgba(99,179,237,0.12);
                    border-radius:10px;padding:0.8rem;text-align:center;margin-bottom:0.5rem;">
                    <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
                         background:linear-gradient(135deg,#10b981,#38bdf8);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;">{searches_count}</div>
                    <div style="color:#4b5563;font-size:0.62rem;font-weight:600;
                         letter-spacing:0.08em;text-transform:uppercase;margin-top:2px;">Searches</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""<div style="background:#111827;border:1px solid rgba(99,179,237,0.12);
                border-radius:10px;padding:0.7rem 1rem;display:flex;align-items:center;
                justify-content:space-between;margin-bottom:0.5rem;">
                <span style="color:#94a3b8;font-size:0.78rem;">Competitors tracked</span>
                <span style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
                     color:#38bdf8;">{competitors_tracked}</span>
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown("<hr style='margin:1rem 0;'>", unsafe_allow_html=True)

        # ── API Status ────────────────────────────────
        groq_ok    = bool(st.session_state.get("groq_api_key"))
        tavily_ok  = bool(st.session_state.get("tavily_api_key"))
        serp_ok    = bool(st.session_state.get("serpapi_key"))

        def _dot(ok): return "🟢" if ok else "🔴"

        st.markdown(
            f"""
            <div style="padding:0 1rem;">
                <p style="color:#4b5563;font-size:0.68rem;font-weight:600;letter-spacing:0.1em;
                   text-transform:uppercase;margin-bottom:0.6rem;">API Status</p>
                <div style="display:flex;flex-direction:column;gap:0.35rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="color:#94a3b8;font-size:0.75rem;">Groq LLM</span>
                        <span>{_dot(groq_ok)} <span style="color:#4b5563;font-size:0.7rem;">{'Connected' if groq_ok else 'Not set'}</span></span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="color:#94a3b8;font-size:0.75rem;">Tavily Search</span>
                        <span>{_dot(tavily_ok)} <span style="color:#4b5563;font-size:0.7rem;">{'Connected' if tavily_ok else 'Not set'}</span></span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="color:#94a3b8;font-size:0.75rem;">SerpAPI</span>
                        <span>{_dot(serp_ok)} <span style="color:#4b5563;font-size:0.7rem;">{'Connected' if serp_ok else 'Not set'}</span></span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    return st.session_state.current_page
