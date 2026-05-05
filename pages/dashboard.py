"""pages/dashboard.py — Overview dashboard with key metrics."""

import streamlit as st
from datetime import datetime
import json


def render_dashboard():
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="page-title">Intelligence Dashboard</div>
        <div class="page-subtitle">Real-time overview of your competitive intelligence portfolio</div>
        """,
        unsafe_allow_html=True,
    )

    reports      = st.session_state.get("reports", [])
    competitors  = st.session_state.get("tracked_competitors", [])
    search_count = st.session_state.get("search_count", 0)

    # ── KPI Metrics ───────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-number">{len(reports)}</div>
                <div class="metric-label">Total Reports</div>
                <div class="metric-delta up">↑ Active session</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-number">{len(competitors)}</div>
                <div class="metric-label">Competitors Tracked</div>
                <div class="metric-delta" style="color:var(--text-muted);">Across all reports</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-number">{search_count}</div>
                <div class="metric-label">Searches Run</div>
                <div class="metric-delta up">↑ This session</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with col4:
        # Calculate average threat level across all reports
        threat_scores = []
        for r in reports:
            for c in r.get("competitors", []):
                tl = c.get("threat_level")
                if isinstance(tl, (int, float)):
                    threat_scores.append(tl)
        avg_threat = round(sum(threat_scores) / len(threat_scores), 1) if threat_scores else 0
        threat_color = "var(--accent-red)" if avg_threat >= 7 else "var(--accent-amber)" if avg_threat >= 4 else "var(--accent-green)"

        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-number" style="background:none;-webkit-text-fill-color:{threat_color};">{avg_threat}</div>
                <div class="metric-label">Avg Threat Level</div>
                <div class="metric-delta" style="color:{threat_color};">{'High' if avg_threat>=7 else 'Medium' if avg_threat>=4 else 'Low'} Risk</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Quick-start CTA ───────────────────────────────────────────────────────
    if not reports:
        st.markdown(
            """
            <div class="intel-card" style="text-align:center;padding:2.5rem;
                 background:linear-gradient(135deg,rgba(56,189,248,0.04),rgba(139,92,246,0.04));
                 border:1px dashed rgba(99,179,237,0.25);">
                <div style="font-size:2.5rem;margin-bottom:0.8rem;">🔍</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;
                     color:#f0f4ff;margin-bottom:0.5rem;">No intelligence reports yet</div>
                <div style="color:#94a3b8;font-size:0.875rem;max-width:400px;margin:0 auto 1.5rem;">
                    Start by navigating to <strong style="color:#38bdf8">Research</strong> to run your
                    first competitive analysis. The AI agent will gather, analyze, and synthesize
                    market intelligence for you automatically.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🚀  Start Research Now", use_container_width=False):
            st.session_state.current_page = "Research"
            st.rerun()
        return

    # ── Recent Reports ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Recent Reports</div>', unsafe_allow_html=True)

    for report in reversed(reports[-5:]):
        _report_card(report)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Threat Map ────────────────────────────────────────────────────────────
    all_comps = []
    for r in reports:
        for c in r.get("competitors", []):
            c["_report"] = r.get("your_company", "")
            all_comps.append(c)

    if all_comps:
        st.markdown('<div class="section-title">⚠️ Threat Overview</div>', unsafe_allow_html=True)

        sorted_comps = sorted(all_comps, key=lambda x: x.get("threat_level", 0), reverse=True)
        for comp in sorted_comps[:8]:
            tl = comp.get("threat_level", 5)
            tl_norm = min(max(tl, 1), 10)
            bar_width = tl_norm * 10
            bar_color = "#ef4444" if tl >= 7 else "#f59e0b" if tl >= 4 else "#10b981"

            st.markdown(
                f"""<div class="intel-card" style="padding:1rem 1.4rem;margin-bottom:0.5rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                        <div>
                            <span style="font-weight:600;color:#f0f4ff;">{comp.get('company_name','Unknown')}</span>
                            <span style="color:#4b5563;font-size:0.75rem;margin-left:0.5rem;">
                                vs {comp.get('_report','')}
                            </span>
                        </div>
                        <span style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:{bar_color};">
                            {tl}/10
                        </span>
                    </div>
                    <div style="background:rgba(255,255,255,0.05);border-radius:4px;height:5px;overflow:hidden;">
                        <div style="width:{bar_width}%;height:100%;background:{bar_color};
                             border-radius:4px;transition:width 0.3s;"></div>
                    </div>
                    <div style="color:#4b5563;font-size:0.72rem;margin-top:0.4rem;">
                        {comp.get('market_positioning','N/A')[:100]}
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    # ── Bottom: Settings reminder ─────────────────────────────────────────────
    groq_ok   = bool(st.session_state.get("groq_api_key"))
    tavily_ok = bool(st.session_state.get("tavily_api_key"))
    if not (groq_ok and tavily_ok):
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.warning(
            "⚠️ **API keys not fully configured.** Reports will use demo data. "
            "Go to **Settings** to add your Groq + Tavily API keys."
        )


# ── Helper: single report card ────────────────────────────────────────────────

def _report_card(report: dict):
    comps = report.get("competitors", [])
    date  = report.get("created_at", "")[:10]
    company = report.get("your_company", "—")
    industry = report.get("industry", "—")
    n_comps = len(comps)

    avg_threat = 0
    if comps:
        scores = [c.get("threat_level", 5) for c in comps if isinstance(c.get("threat_level"), (int, float))]
        avg_threat = round(sum(scores) / len(scores), 1) if scores else 0

    threat_badge = "badge-red" if avg_threat >= 7 else "badge-amber" if avg_threat >= 4 else "badge-green"
    threat_label = "High Threat" if avg_threat >= 7 else "Medium Threat" if avg_threat >= 4 else "Low Threat"

    st.markdown(
        f"""<div class="intel-card" style="margin-bottom:0.6rem;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
                         color:#f0f4ff;margin-bottom:0.2rem;">{company} Intelligence Report</div>
                    <div style="color:#94a3b8;font-size:0.8rem;">{industry} · {n_comps} competitor{'s' if n_comps != 1 else ''} · {date}</div>
                </div>
                <div style="display:flex;gap:0.4rem;flex-wrap:wrap;justify-content:flex-end;">
                    <span class="badge {threat_badge}">{threat_label}</span>
                    <span class="badge badge-blue">{n_comps} Comps</span>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
