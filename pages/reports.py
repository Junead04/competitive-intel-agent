"""pages/reports.py — View, compare, and export intelligence reports."""

from __future__ import annotations

import json
import io
from datetime import datetime

import streamlit as st


def render_reports():
    st.markdown(
        """
        <div class="page-title">Intelligence Reports</div>
        <div class="page-subtitle">Browse, analyze, and export your saved competitive intelligence reports</div>
        """,
        unsafe_allow_html=True,
    )

    reports = st.session_state.get("reports", [])

    if not reports:
        st.markdown(
            '<div class="intel-card" style="text-align:center;padding:3rem;">'
            '<div style="font-size:2.5rem;margin-bottom:1rem;">📊</div>'
            '<div style="font-family:\'Syne\',sans-serif;font-size:1.1rem;font-weight:700;'
            'color:#f0f4ff;margin-bottom:0.5rem;">No reports yet</div>'
            '<div style="color:#94a3b8;">Run competitive research to generate your first report.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("→ Go to Research"):
            st.session_state.current_page = "Research"
            st.rerun()
        return

    # ── Report Selector ───────────────────────────────────────────────────────
    report_labels = [
        f"{r.get('your_company','?')} — {r.get('created_at','')[:10]}  ({len(r.get('competitors',[]))} competitors)"
        for r in reports
    ]

    selected_idx = st.selectbox(
        "Select Report",
        range(len(reports)),
        format_func=lambda i: report_labels[i],
        index=len(reports) - 1,
    )
    report = reports[selected_idx]

    # ── Report Header ─────────────────────────────────────────────────────────
    your_company = report.get("your_company", "—")
    industry     = report.get("industry", "—")
    created_at   = report.get("created_at", "")[:19].replace("T", " ")
    depth        = report.get("depth", "standard")
    competitors  = report.get("competitors", [])
    synthesis    = report.get("synthesis", {})

    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(
            f'<div class="intel-card" style="margin-bottom:0">'
            f'<div style="font-family:\'Syne\',sans-serif;font-size:1.4rem;font-weight:800;'
            f'color:#f0f4ff;margin-bottom:0.3rem;">{your_company} Competitive Intelligence</div>'
            f'<div style="color:#94a3b8;font-size:0.82rem;">'
            f'📁 {industry} &nbsp;·&nbsp; 📅 {created_at} &nbsp;·&nbsp; 🔍 {depth.title()} depth</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_h2:
        _export_buttons(report)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = st.tabs(["📋 Overview", "🏢 Competitors", "⚖️ Comparison", "💡 Insights", "📄 Raw"])

    with tabs[0]:
        _render_overview(report, synthesis, competitors)

    with tabs[1]:
        _render_competitors_tab(competitors)

    with tabs[2]:
        _render_comparison_tab(competitors, synthesis)

    with tabs[3]:
        _render_insights_tab(synthesis)

    with tabs[4]:
        st.code(json.dumps(report, indent=2, default=str), language="json")


# ── Tab: Overview ─────────────────────────────────────────────────────────────

def _render_overview(report, synthesis, competitors):
    # Quick metrics row
    threat_scores = [c.get("threat_level", 5) for c in competitors if isinstance(c.get("threat_level"), (int, float))]
    avg_threat = round(sum(threat_scores) / len(threat_scores), 1) if threat_scores else 0
    top_threat = max(competitors, key=lambda x: x.get("threat_level", 0), default={}) if competitors else {}

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-number">{len(competitors)}</div>'
            f'<div class="metric-label">Competitors Analyzed</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        tc = "#ef4444" if avg_threat >= 7 else "#f59e0b" if avg_threat >= 4 else "#10b981"
        st.markdown(
            f'<div class="metric-card"><div class="metric-number" style="-webkit-text-fill-color:{tc}">'
            f'{avg_threat}</div><div class="metric-label">Average Threat Score</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        tname = top_threat.get("company_name", "—")
        st.markdown(
            f'<div class="metric-card"><div class="metric-number" style="font-size:1.2rem;'
            f'-webkit-text-fill-color:#ef4444;">{tname}</div>'
            f'<div class="metric-label">Highest Threat</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Executive summary
    exec_sum = synthesis.get("executive_summary", "")
    if exec_sum:
        st.markdown('<div class="section-title">📝 Executive Summary</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="intel-card" style="line-height:1.9;color:var(--text-secondary);'
            f'font-size:0.9rem;">{exec_sum}</div>',
            unsafe_allow_html=True,
        )

    # Whitespace opportunities
    opportunities = synthesis.get("whitespace_opportunities", [])
    if opportunities:
        st.markdown('<div class="section-title" style="margin-top:1.2rem;">🌟 Market Opportunities</div>', unsafe_allow_html=True)
        for opp in opportunities:
            st.markdown(
                f'<div class="insight-block success">💡 {opp}</div>',
                unsafe_allow_html=True,
            )


# ── Tab: Competitors ──────────────────────────────────────────────────────────

def _render_competitors_tab(competitors):
    for comp in competitors:
        name       = comp.get("company_name", "Unknown")
        tl         = comp.get("threat_level", 5)
        summary    = comp.get("overall_summary", "N/A")
        strengths  = comp.get("strengths", [])
        weaknesses = comp.get("weaknesses", [])
        opp        = comp.get("opportunities", [])
        threats    = comp.get("threats", [])
        news       = comp.get("recent_news", [])
        pricing    = comp.get("pricing_tiers", [])
        products   = comp.get("core_products", [])
        positioning = comp.get("market_positioning", "")
        tech       = comp.get("tech_stack", [])

        tl_color   = "#ef4444" if tl >= 7 else "#f59e0b" if tl >= 4 else "#10b981"
        tl_badge   = "badge-red" if tl >= 7 else "badge-amber" if tl >= 4 else "badge-green"

        st.markdown(
            f'<div style="display:flex;align-items:center;gap:1rem;margin:1rem 0 0.5rem;">'
            f'<span style="font-family:\'Syne\',sans-serif;font-size:1.15rem;font-weight:800;'
            f'color:#f0f4ff;">🏢 {name}</span>'
            f'<span class="badge {tl_badge}">Threat {tl}/10</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        with st.expander("View Full Profile", expanded=False):
            if positioning:
                st.markdown(
                    f'<div class="insight-block"><strong>Market Position:</strong> {positioning}</div>',
                    unsafe_allow_html=True,
                )

            col1, col2 = st.columns(2)
            with col1:
                if strengths:
                    st.markdown("**✅ Strengths**")
                    for s in strengths:
                        st.markdown(f"- {s}")
                if opp:
                    st.markdown("**🌟 Opportunities**")
                    for o in opp:
                        st.markdown(f"- {o}")
            with col2:
                if weaknesses:
                    st.markdown("**⚠️ Weaknesses**")
                    for w in weaknesses:
                        st.markdown(f"- {w}")
                if threats:
                    st.markdown("**🔴 Threats**")
                    for t in threats:
                        st.markdown(f"- {t}")

            if products:
                st.markdown("**📦 Core Products**")
                st.markdown(", ".join(products))

            if tech:
                st.markdown("**⚙️ Tech Stack**")
                chips = "".join(
                    f'<span class="competitor-chip">{t}</span>' for t in tech
                )
                st.markdown(f'<div style="display:flex;flex-wrap:wrap;">{chips}</div>', unsafe_allow_html=True)

            if pricing:
                st.markdown("**💰 Pricing Tiers**")
                pcols = st.columns(min(len(pricing), 5))
                for i, tier in enumerate(pricing[:5]):
                    with pcols[i]:
                        if isinstance(tier, dict):
                            tier_name  = tier.get("name", f"Tier {i+1}")
                            tier_price = tier.get("price", "—")
                            tier_desc  = tier.get("description", "")
                        else:
                            tier_name, tier_price, tier_desc = str(tier), "—", ""
                        st.markdown(
                            f'<div style="background:var(--bg-secondary);border:1px solid var(--border);'
                            f'border-radius:10px;padding:0.8rem;text-align:center;">'
                            f'<div style="font-weight:700;color:#f0f4ff;font-size:0.85rem;">{tier_name}</div>'
                            f'<div style="color:var(--accent-cyan);font-weight:600;margin:0.3rem 0;">{tier_price}</div>'
                            f'<div style="color:var(--text-muted);font-size:0.72rem;">{tier_desc[:60]}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            if news:
                st.markdown("**📰 Recent News**")
                for item in news[:4]:
                    if isinstance(item, dict):
                        title = item.get("title", "")
                        date  = item.get("date", "")
                        summ  = item.get("summary", "")
                    else:
                        title, date, summ = str(item), "", ""
                    date_html = ("<br><span style='color:var(--text-muted);font-size:0.75rem;'>" + date + "</span>") if date else ""
                    summ_html = ("<br>" + summ) if summ else ""
                    st.markdown(
                        f'<div class="insight-block" style="margin-bottom:0.4rem;">'
                        f'<strong>{title}</strong>'
                        f'{date_html}'
                        f'{summ_html}</div>',
                        unsafe_allow_html=True,
                    )

            if summary:
                st.markdown("**📋 Summary**")
                st.markdown(
                    f'<div class="insight-block">{summary}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<hr>", unsafe_allow_html=True)


# ── Tab: Comparison ───────────────────────────────────────────────────────────

def _render_comparison_tab(competitors, synthesis):
    st.markdown('<div class="section-title">⚖️ Side-by-Side Comparison</div>', unsafe_allow_html=True)

    matrix = synthesis.get("competitive_matrix", [])

    if matrix:
        import pandas as pd
        try:
            df = pd.DataFrame(matrix)
            numeric_cols = [c for c in df.columns if c != "company"]
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
            st.dataframe(
                df.style.background_gradient(cmap="Blues", subset=numeric_cols),
                use_container_width=True,
                hide_index=True,
            )
        except Exception:
            st.json(matrix)
    else:
        # Build a simple comparison table from raw data
        import pandas as pd
        rows = []
        for c in competitors:
            tl = c.get("threat_level", "?")
            rows.append({
                "Company": c.get("company_name", "?"),
                "Market Positioning": c.get("market_positioning", "—")[:60],
                "Threat Level": tl,
                "Products": len(c.get("core_products", [])),
                "Pricing Tiers": len(c.get("pricing_tiers", [])),
                "Strengths": len(c.get("strengths", [])),
                "Weaknesses": len(c.get("weaknesses", [])),
            })
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # Threats ranking
    threat_rank = synthesis.get("threats_ranking", [])
    if threat_rank:
        st.markdown('<div class="section-title" style="margin-top:1.2rem;">🏆 Threat Ranking</div>', unsafe_allow_html=True)
        for i, item in enumerate(threat_rank, 1):
            if isinstance(item, dict):
                name = item.get("company", item.get("name", f"Company {i}"))
                rationale = item.get("rationale", "")
            else:
                name, rationale = str(item), ""
            badge = "badge-red" if i == 1 else "badge-amber" if i <= 3 else "badge-blue"
            rationale_html = ("<br><span style='color:var(--text-secondary);font-size:0.8rem;'>" + rationale + "</span>") if rationale else ""
            st.markdown(
                f'<div class="intel-card" style="margin-bottom:0.5rem;display:flex;'
                f'align-items:flex-start;gap:1rem;">'
                f'<span style="font-family:\'Syne\',sans-serif;font-size:1.2rem;font-weight:800;'
                f'color:var(--text-muted);min-width:1.5rem;">#{i}</span>'
                f'<div><strong style="color:var(--text-primary);">{name}</strong>'
                f'{rationale_html}'
                f'</div></div>',
                unsafe_allow_html=True,
            )


# ── Tab: Insights ─────────────────────────────────────────────────────────────

def _render_insights_tab(synthesis):
    insights = synthesis.get("key_insights", [])
    recs     = synthesis.get("recommended_actions", [])
    gaps     = synthesis.get("whitespace_opportunities", [])

    if insights:
        st.markdown('<div class="section-title">💡 Key Insights</div>', unsafe_allow_html=True)
        for i, ins in enumerate(insights, 1):
            st.markdown(
                f'<div class="insight-block"><strong>{i}.</strong> {ins}</div>',
                unsafe_allow_html=True,
            )

    if recs:
        st.markdown('<div class="section-title" style="margin-top:1rem;">🎯 Strategic Recommendations</div>', unsafe_allow_html=True)
        for i, rec in enumerate(recs, 1):
            st.markdown(
                f'<div class="insight-block success"><strong>Action {i}:</strong> {rec}</div>',
                unsafe_allow_html=True,
            )

    if gaps:
        st.markdown('<div class="section-title" style="margin-top:1rem;">🌟 Market Gaps & Opportunities</div>', unsafe_allow_html=True)
        for gap in gaps:
            st.markdown(
                f'<div class="insight-block warning">💡 {gap}</div>',
                unsafe_allow_html=True,
            )

    if not (insights or recs or gaps):
        st.info("No insights extracted yet. Run a comprehensive research to populate this section.")


# ── Export helpers ─────────────────────────────────────────────────────────────

def _export_buttons(report: dict):
    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    with st.expander("⬇️ Export"):
        # JSON
        json_str = json.dumps(report, indent=2, default=str)
        st.download_button(
            "📄 JSON",
            data=json_str,
            file_name=f"report_{report.get('id','export')}.json",
            mime="application/json",
            use_container_width=True,
        )

        # Markdown summary
        md = _report_to_markdown(report)
        st.download_button(
            "📝 Markdown",
            data=md,
            file_name=f"report_{report.get('id','export')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

        # CSV of competitor table
        try:
            import pandas as pd
            rows = []
            for c in report.get("competitors", []):
                rows.append({
                    "Company": c.get("company_name"),
                    "Threat Level": c.get("threat_level"),
                    "Market Positioning": c.get("market_positioning"),
                    "Strengths": " | ".join(c.get("strengths", [])),
                    "Weaknesses": " | ".join(c.get("weaknesses", [])),
                    "Products": " | ".join(c.get("core_products", [])),
                })
            csv = pd.DataFrame(rows).to_csv(index=False)
            st.download_button(
                "📊 CSV",
                data=csv,
                file_name=f"competitors_{report.get('id','export')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except Exception:
            pass


def _report_to_markdown(report: dict) -> str:
    lines = [
        f"# Competitive Intelligence Report: {report.get('your_company', '?')}",
        f"**Industry:** {report.get('industry', '?')}",
        f"**Generated:** {report.get('created_at', '?')[:19]}",
        f"**Research Depth:** {report.get('depth', '?').title()}",
        "",
        "---",
        "",
    ]

    synthesis = report.get("synthesis", {})
    if synthesis.get("executive_summary"):
        lines += ["## Executive Summary", synthesis["executive_summary"], ""]

    for comp in report.get("competitors", []):
        lines += [
            f"## {comp.get('company_name', 'Unknown')}",
            f"**Threat Level:** {comp.get('threat_level', '?')}/10",
            f"**Market Positioning:** {comp.get('market_positioning', '?')}",
            "",
            "### Strengths",
        ]
        for s in comp.get("strengths", []):
            lines.append(f"- {s}")
        lines += ["", "### Weaknesses"]
        for w in comp.get("weaknesses", []):
            lines.append(f"- {w}")
        lines += ["", comp.get("overall_summary", ""), "", "---", ""]

    if synthesis.get("key_insights"):
        lines += ["## Key Insights"]
        for i, ins in enumerate(synthesis["key_insights"], 1):
            lines.append(f"{i}. {ins}")
        lines.append("")

    if synthesis.get("recommended_actions"):
        lines += ["## Recommended Actions"]
        for i, rec in enumerate(synthesis["recommended_actions"], 1):
            lines.append(f"{i}. {rec}")

    return "\n".join(lines)
