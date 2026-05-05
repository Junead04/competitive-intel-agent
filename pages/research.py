"""pages/research.py — Run competitive research with the AI agent."""

from __future__ import annotations

import time
import streamlit as st
from datetime import datetime


# ── Lazy import agent to avoid import errors when keys missing ────────────────

def _get_agent():
    from agents.intel_agent import IntelAgent
    return IntelAgent


def render_research():
    st.markdown(
        """
        <div class="page-title">Competitive Research</div>
        <div class="page-subtitle">Configure your research parameters and launch the AI intelligence agent</div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["⚙️  Configure", "🤖  Agent Run", "📄  Raw Results"])

    with tabs[0]:
        _render_configure_tab()

    with tabs[1]:
        _render_agent_tab()

    with tabs[2]:
        _render_raw_tab()


# ── Tab 1: Configure ──────────────────────────────────────────────────────────

def _render_configure_tab():
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-title">🏢 Your Company</div>', unsafe_allow_html=True)

        your_company = st.text_input(
            "Company Name",
            value=st.session_state.get("cfg_your_company", ""),
            placeholder="e.g. Acme Corp",
            help="Your company name — used for context in all research queries.",
        )
        st.session_state.cfg_your_company = your_company

        industry = st.text_input(
            "Industry / Market",
            value=st.session_state.get("cfg_industry", ""),
            placeholder="e.g. B2B SaaS, FinTech, E-Commerce",
        )
        st.session_state.cfg_industry = industry

        st.markdown('<div class="section-title" style="margin-top:1.2rem;">🎯 Competitors</div>', unsafe_allow_html=True)

        competitors_raw = st.text_area(
            "Competitor Names (one per line)",
            value=st.session_state.get("cfg_competitors_raw", ""),
            placeholder="Salesforce\nHubSpot\nZoho CRM\nPipedrive",
            height=130,
            help="Enter one competitor name per line. Up to 10 recommended.",
        )
        st.session_state.cfg_competitors_raw = competitors_raw

        # Parse competitors
        competitor_list = [c.strip() for c in competitors_raw.strip().splitlines() if c.strip()]

        if competitor_list:
            st.markdown(
                "<div style='display:flex;flex-wrap:wrap;gap:0.3rem;margin-top:0.3rem;'>",
                unsafe_allow_html=True,
            )
            chips = "".join(
                f'<span class="competitor-chip">🏢 {c}</span>' for c in competitor_list
            )
            st.markdown(chips + "</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-title" style="margin-top:1.2rem;">🔎 Focus Areas</div>', unsafe_allow_html=True)

        focus_options = [
            "Pricing & Packaging",
            "Product Features",
            "Recent News & Announcements",
            "Funding & Financials",
            "Customer Reviews",
            "Go-to-Market Strategy",
            "Technology Stack",
            "Leadership & Team",
            "Partnerships & Integrations",
            "Geographic Expansion",
        ]

        selected_focus = st.multiselect(
            "Select research focus areas",
            focus_options,
            default=st.session_state.get("cfg_focus", focus_options[:4]),
        )
        st.session_state.cfg_focus = selected_focus

    with col_right:
        st.markdown('<div class="section-title">⚡ Research Settings</div>', unsafe_allow_html=True)

        depth = st.selectbox(
            "Research Depth",
            ["quick", "standard", "comprehensive"],
            index=["quick", "standard", "comprehensive"].index(
                st.session_state.get("report_depth", "standard")
            ),
            help="Quick: 3 searches/competitor | Standard: 5 | Comprehensive: 8+",
        )
        st.session_state.report_depth = depth

        max_iters = {"quick": 4, "standard": 6, "comprehensive": 10}[depth]
        st.markdown(
            f'<div class="insight-block">Depth: <strong>{depth.title()}</strong> — '
            f'up to <strong>{max_iters} search iterations</strong> per competitor</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-title" style="margin-top:1rem;">🔐 API Configuration</div>', unsafe_allow_html=True)

        groq_ok   = bool(st.session_state.get("groq_api_key"))
        tavily_ok = bool(st.session_state.get("tavily_api_key"))
        serp_ok   = bool(st.session_state.get("serpapi_key"))

        def _status(ok, name):
            icon  = "✅" if ok else "❌"
            color = "var(--accent-green)" if ok else "var(--accent-red)"
            hint  = "Ready" if ok else "Not set — go to Settings"
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:0.4rem 0;'
                f'border-bottom:1px solid var(--border);">'
                f'<span style="color:var(--text-secondary);font-size:0.82rem;">{icon} {name}</span>'
                f'<span style="color:{color};font-size:0.75rem;">{hint}</span></div>',
                unsafe_allow_html=True,
            )

        _status(groq_ok,   "Groq LLM")
        _status(tavily_ok, "Tavily Search")
        _status(serp_ok,   "SerpAPI (optional)")

        if not groq_ok:
            st.warning("⚠️ Groq API key required. Add it in **Settings**.")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # Launch button
        can_run = bool(competitor_list and your_company)
        if not can_run:
            st.info("Fill in your company name and at least one competitor to proceed.")

        if st.button("🚀  Launch Research Agent", disabled=not can_run, use_container_width=True):
            # Save config to session
            st.session_state.cfg_competitor_list = competitor_list
            st.session_state.research_running    = True
            st.session_state.agent_logs          = []
            st.session_state.current_research    = None
            st.session_state.current_page_tab    = 1  # switch to Agent Run tab
            st.rerun()

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # Estimated time
        n = len(competitor_list)
        est_min = max(1, n * (2 if depth == "quick" else 4 if depth == "standard" else 7))
        st.markdown(
            f'<div class="insight-block" style="margin-top:0.5rem;">'
            f'⏱ Estimated time: <strong>{est_min}–{est_min+2} minutes</strong> '
            f'for {n} competitor{"s" if n!=1 else ""}</div>',
            unsafe_allow_html=True,
        )


# ── Tab 2: Agent Run ──────────────────────────────────────────────────────────

def _render_agent_tab():
    if not st.session_state.get("research_running") and not st.session_state.get("current_research"):
        st.markdown(
            '<div class="intel-card" style="text-align:center;padding:3rem;">'
            '<div style="font-size:2rem;margin-bottom:1rem;">🤖</div>'
            '<div style="color:var(--text-secondary);">Configure your research in the <strong>Configure</strong> tab and launch the agent.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    if st.session_state.get("research_running"):
        _run_agent()

    # Show agent logs
    logs = st.session_state.get("agent_logs", [])
    if logs:
        st.markdown('<div class="section-title">🖥️ Agent Activity Log</div>', unsafe_allow_html=True)

        log_html = ""
        for entry in logs:
            msg, kind = entry["msg"], entry["kind"]
            ts = entry.get("ts", "")
            css = {"step": "log-step", "tool": "log-tool", "result": "log-result",
                   "warn": "log-warn", "error": "log-error"}.get(kind, "")
            log_html += f'<div><span class="log-time">{ts}</span> <span class="{css}">{msg}</span></div>\n'

        st.markdown(f'<div class="agent-log">{log_html}</div>', unsafe_allow_html=True)

    # Results
    if st.session_state.get("current_research"):
        _display_research_results(st.session_state.current_research)


def _run_agent():
    """Execute the agent and update session state."""
    competitor_list = st.session_state.get("cfg_competitor_list", [])
    your_company    = st.session_state.get("cfg_your_company", "MyCompany")
    industry        = st.session_state.get("cfg_industry", "Technology")
    focus_areas     = st.session_state.get("cfg_focus", [])

    groq_key   = st.session_state.get("groq_api_key", "")
    tavily_key = st.session_state.get("tavily_api_key", "")
    serpapi_key = st.session_state.get("serpapi_key", "")
    model       = st.session_state.get("llm_model", "llama3-70b-8192")
    temperature = st.session_state.get("temperature", 0.3)
    max_results = st.session_state.get("max_search_results", 5)

    logs: list[dict] = []

    def log(msg: str, kind: str = "step"):
        ts = datetime.now().strftime("%H:%M:%S")
        logs.append({"msg": msg, "kind": kind, "ts": ts})
        st.session_state.agent_logs = logs

    log("🚀 CompeteIQ Agent initializing...", "step")

    progress_container = st.empty()
    status_container   = st.empty()

    IntelAgent = _get_agent()

    agent = IntelAgent(
        groq_key    = groq_key,
        tavily_key  = tavily_key or None,
        serpapi_key = serpapi_key or None,
        model       = model,
        temperature = temperature,
        max_results = max_results,
        log_callback = log,
    )

    competitor_results = []
    total = len(competitor_list)

    for i, comp in enumerate(competitor_list):
        pct = int((i / total) * 85)
        progress_container.progress(pct, text=f"Researching {comp}... ({i+1}/{total})")
        status_container.markdown(
            f'<div class="insight-block">🔍 Analyzing <strong>{comp}</strong>...</div>',
            unsafe_allow_html=True,
        )

        data = agent.research_competitor(comp, your_company, focus_areas)
        competitor_results.append(data)

        # Track globally
        tracked = st.session_state.get("tracked_competitors", [])
        if comp not in tracked:
            tracked.append(comp)
        st.session_state.tracked_competitors = tracked
        st.session_state.search_count = st.session_state.get("search_count", 0) + max_results

    # Synthesis
    progress_container.progress(90, text="Synthesizing cross-competitor analysis...")
    status_container.markdown(
        '<div class="insight-block">⚡ Generating synthesis report...</div>',
        unsafe_allow_html=True,
    )

    synthesis = agent.synthesize_report(competitor_results, your_company, industry)

    progress_container.progress(100, text="✅ Research complete!")
    status_container.empty()

    # Save report
    report = {
        "your_company":  your_company,
        "industry":      industry,
        "focus_areas":   focus_areas,
        "competitors":   competitor_results,
        "synthesis":     synthesis,
        "created_at":    datetime.now().isoformat(),
        "depth":         st.session_state.get("report_depth", "standard"),
        "id":            f"report_{int(time.time())}",
    }

    reports = st.session_state.get("reports", [])
    reports.append(report)
    st.session_state.reports          = reports
    st.session_state.current_research = report
    st.session_state.research_running = False

    log("✅ All research complete. Report saved.", "result")
    st.rerun()


# ── Display Results ───────────────────────────────────────────────────────────

def _display_research_results(report: dict):
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Research Results</div>', unsafe_allow_html=True)

    competitors = report.get("competitors", [])
    synthesis   = report.get("synthesis", {})

    # Executive summary
    if synthesis.get("executive_summary"):
        st.markdown(
            f'<div class="intel-card" style="margin-bottom:1rem;">'
            f'<div style="color:var(--accent-cyan);font-size:0.75rem;font-weight:600;'
            f'letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.6rem;">Executive Summary</div>'
            f'<div style="color:var(--text-secondary);line-height:1.8;font-size:0.875rem;">'
            f'{synthesis["executive_summary"]}</div></div>',
            unsafe_allow_html=True,
        )

    # Per-competitor cards
    for comp in competitors:
        _competitor_result_card(comp)

    # Key insights
    insights = synthesis.get("key_insights", [])
    if insights:
        st.markdown('<div class="section-title">💡 Key Strategic Insights</div>', unsafe_allow_html=True)
        for i, insight in enumerate(insights, 1):
            st.markdown(
                f'<div class="insight-block"><strong>{i}.</strong> {insight}</div>',
                unsafe_allow_html=True,
            )

    # Recommendations
    recs = synthesis.get("recommended_actions", [])
    if recs:
        st.markdown('<div class="section-title">🎯 Recommended Actions</div>', unsafe_allow_html=True)
        for i, rec in enumerate(recs, 1):
            st.markdown(
                f'<div class="insight-block success"><strong>Action {i}:</strong> {rec}</div>',
                unsafe_allow_html=True,
            )

    # Save to Reports button
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("📊 View Full Report →  Go to Reports", use_container_width=True):
            st.session_state.current_page = "Reports"
            st.rerun()
    with col2:
        if st.button("🔄 New Research", use_container_width=True):
            st.session_state.current_research = None
            st.session_state.agent_logs       = []
            st.rerun()


def _competitor_result_card(comp: dict):
    name      = comp.get("company_name", "Unknown")
    tl        = comp.get("threat_level", 5)
    summary   = comp.get("overall_summary", "")[:300]
    strengths = comp.get("strengths", [])[:3]
    weaknesses = comp.get("weaknesses", [])[:3]
    tl_color  = "#ef4444" if tl >= 7 else "#f59e0b" if tl >= 4 else "#10b981"

    with st.expander(f"🏢 {name}  —  Threat Level {tl}/10", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                '<div style="color:var(--accent-green);font-size:0.75rem;font-weight:600;'
                'letter-spacing:0.05em;margin-bottom:0.4rem;">STRENGTHS</div>',
                unsafe_allow_html=True,
            )
            for s in strengths:
                st.markdown(f"✅ {s}")
        with col2:
            st.markdown(
                '<div style="color:var(--accent-red);font-size:0.75rem;font-weight:600;'
                'letter-spacing:0.05em;margin-bottom:0.4rem;">WEAKNESSES</div>',
                unsafe_allow_html=True,
            )
            for w in weaknesses:
                st.markdown(f"⚠️ {w}")

        if summary:
            st.markdown(
                f'<div class="insight-block" style="margin-top:0.8rem;">{summary}…</div>',
                unsafe_allow_html=True,
            )

        # Pricing tiers
        pricing = comp.get("pricing_tiers", [])
        if pricing:
            st.markdown("**💰 Pricing**")
            pcols = st.columns(min(len(pricing), 4))
            for i, tier in enumerate(pricing[:4]):
                with pcols[i]:
                    tier_name  = tier.get("name", f"Tier {i+1}") if isinstance(tier, dict) else str(tier)
                    tier_price = tier.get("price", "—")          if isinstance(tier, dict) else "—"
                    st.markdown(
                        f'<div style="background:var(--bg-secondary);border:1px solid var(--border);'
                        f'border-radius:8px;padding:0.6rem;text-align:center;">'
                        f'<div style="font-weight:600;color:var(--text-primary);">{tier_name}</div>'
                        f'<div style="color:var(--accent-cyan);font-size:0.85rem;">{tier_price}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


# ── Tab 3: Raw Results ────────────────────────────────────────────────────────

def _render_raw_tab():
    import json
    research = st.session_state.get("current_research")
    if not research:
        st.info("No research results yet.")
        return

    st.markdown('<div class="section-title">🗂️ Raw JSON Output</div>', unsafe_allow_html=True)
    st.code(json.dumps(research, indent=2, default=str), language="json")

    # Download
    json_str = json.dumps(research, indent=2, default=str)
    st.download_button(
        "⬇️ Download JSON",
        data=json_str,
        file_name=f"intel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
    )
