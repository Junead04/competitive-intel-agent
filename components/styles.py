import streamlit as st


def inject_styles():
    st.markdown(
        """
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

    /* ── CSS Variables ── */
    :root {
        --bg-primary:    #080c14;
        --bg-secondary:  #0d1420;
        --bg-card:       #111827;
        --bg-card-hover: #161f30;
        --border:        rgba(99, 179, 237, 0.12);
        --border-bright: rgba(99, 179, 237, 0.35);
        --accent-cyan:   #38bdf8;
        --accent-blue:   #3b82f6;
        --accent-violet: #8b5cf6;
        --accent-green:  #10b981;
        --accent-amber:  #f59e0b;
        --accent-red:    #ef4444;
        --text-primary:  #f0f4ff;
        --text-secondary:#94a3b8;
        --text-muted:    #4b5563;
        --gradient-1: linear-gradient(135deg, #38bdf8 0%, #3b82f6 50%, #8b5cf6 100%);
        --gradient-2: linear-gradient(135deg, #10b981 0%, #38bdf8 100%);
        --shadow-glow:   0 0 40px rgba(56, 189, 248, 0.08);
        --radius-card:   14px;
        --radius-sm:     8px;
    }

    /* ── Base Reset ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    .main .block-container {
        padding: 1.5rem 2.5rem 3rem;
        max-width: 1400px;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.3); border-radius: 4px; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.4) !important;
    }
    [data-testid="stSidebar"] > div { padding: 0 !important; }

    /* ── Top Header Bar ── */
    [data-testid="stHeader"] {
        background: var(--bg-primary) !important;
        border-bottom: 1px solid var(--border) !important;
    }

    /* ── Cards ── */
    .intel-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 1.4rem 1.6rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-glow);
    }
    .intel-card:hover {
        border-color: var(--border-bright);
        background: var(--bg-card-hover);
        transform: translateY(-1px);
        box-shadow: 0 8px 32px rgba(56,189,248,0.1);
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 1.2rem 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: var(--gradient-1);
    }
    .metric-number {
        font-family: 'Syne', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    .metric-label {
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-secondary);
        margin-top: 0.4rem;
    }
    .metric-delta {
        font-size: 0.78rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    .metric-delta.up   { color: var(--accent-green); }
    .metric-delta.down { color: var(--accent-red); }

    /* ── Page Title ── */
    .page-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.9rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: var(--text-primary);
        margin-bottom: 0.2rem;
    }
    .page-subtitle {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-bottom: 1.8rem;
        font-weight: 300;
    }

    /* ── Section Headers ── */
    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: var(--accent-cyan);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border);
        margin-left: 0.5rem;
    }

    /* ── Status Badges ── */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.2rem 0.65rem;
        border-radius: 99px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .badge-green  { background: rgba(16,185,129,0.15);  color: var(--accent-green);  border: 1px solid rgba(16,185,129,0.3);  }
    .badge-blue   { background: rgba(59,130,246,0.15);  color: var(--accent-blue);   border: 1px solid rgba(59,130,246,0.3);  }
    .badge-amber  { background: rgba(245,158,11,0.15);  color: var(--accent-amber);  border: 1px solid rgba(245,158,11,0.3);  }
    .badge-red    { background: rgba(239,68,68,0.15);   color: var(--accent-red);    border: 1px solid rgba(239,68,68,0.3);   }
    .badge-violet { background: rgba(139,92,246,0.15);  color: var(--accent-violet); border: 1px solid rgba(139,92,246,0.3);  }

    /* ── Buttons ── */
    .stButton > button {
        background: var(--gradient-1) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 0.55rem 1.4rem !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 16px rgba(56,189,248,0.2) !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 24px rgba(56,189,248,0.35) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── Secondary button ── */
    .btn-secondary > button {
        background: transparent !important;
        border: 1px solid var(--border-bright) !important;
        color: var(--accent-cyan) !important;
        box-shadow: none !important;
    }
    .btn-secondary > button:hover {
        background: rgba(56,189,248,0.06) !important;
        box-shadow: 0 0 16px rgba(56,189,248,0.12) !important;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 0 2px rgba(56,189,248,0.12) !important;
    }

    /* ── Labels ── */
    .stTextInput label, .stTextArea label,
    .stSelectbox label, .stMultiSelect label,
    .stSlider label, .stNumberInput label {
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary) !important;
        border-radius: var(--radius-card) !important;
        border: 1px solid var(--border) !important;
        padding: 4px !important;
        gap: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.15s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: transparent !important;
        padding: 1.2rem 0 0 !important;
    }

    /* ── Progress / Spinners ── */
    .stProgress > div > div > div > div {
        background: var(--gradient-1) !important;
    }
    .stSpinner > div { color: var(--accent-cyan) !important; }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
    }
    .streamlit-expanderContent {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
    }

    /* ── Dataframes / Tables ── */
    .stDataFrame { border-radius: var(--radius-card) !important; overflow: hidden !important; }
    .stDataFrame > div { background: var(--bg-card) !important; }
    iframe[title="st.dataframe"] { border-radius: var(--radius-card) !important; }

    /* ── Alerts ── */
    .stAlert { border-radius: var(--radius-card) !important; border-left: 3px solid !important; }
    .stSuccess { border-color: var(--accent-green) !important; background: rgba(16,185,129,0.08) !important; }
    .stWarning { border-color: var(--accent-amber) !important; background: rgba(245,158,11,0.08) !important; }
    .stError   { border-color: var(--accent-red)   !important; background: rgba(239,68,68,0.08)  !important; }
    .stInfo    { border-color: var(--accent-cyan)  !important; background: rgba(56,189,248,0.08) !important; }

    /* ── Dividers ── */
    hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

    /* ── Agent log terminal ── */
    .agent-log {
        background: #050810;
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 1.2rem 1.4rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.78rem;
        color: #64ffda;
        max-height: 320px;
        overflow-y: auto;
        line-height: 1.7;
    }
    .agent-log .log-step   { color: var(--accent-cyan); }
    .agent-log .log-tool   { color: var(--accent-violet); }
    .agent-log .log-result { color: var(--accent-green); }
    .agent-log .log-warn   { color: var(--accent-amber); }
    .agent-log .log-error  { color: var(--accent-red); }
    .agent-log .log-time   { color: var(--text-muted); font-size: 0.68rem; }

    /* ── Competitor card ── */
    .competitor-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 99px;
        padding: 0.3rem 0.9rem;
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-secondary);
        margin: 0.2rem;
        transition: all 0.15s ease;
    }
    .competitor-chip:hover {
        border-color: var(--accent-cyan);
        color: var(--accent-cyan);
    }

    /* ── Intel Insight block ── */
    .insight-block {
        border-left: 3px solid var(--accent-cyan);
        padding: 0.8rem 1.2rem;
        background: rgba(56,189,248,0.04);
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        margin-bottom: 0.8rem;
        font-size: 0.875rem;
        line-height: 1.7;
        color: var(--text-secondary);
    }
    .insight-block strong { color: var(--text-primary); }
    .insight-block.warning { border-color: var(--accent-amber); background: rgba(245,158,11,0.04); }
    .insight-block.danger  { border-color: var(--accent-red);   background: rgba(239,68,68,0.04); }
    .insight-block.success { border-color: var(--accent-green); background: rgba(16,185,129,0.04); }

    /* ── Sidebar Nav ── */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.65rem 1rem;
        border-radius: var(--radius-sm);
        cursor: pointer;
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-secondary);
        transition: all 0.15s ease;
        margin-bottom: 2px;
        border: 1px solid transparent;
    }
    .nav-item:hover {
        background: rgba(56,189,248,0.06);
        color: var(--text-primary);
        border-color: var(--border);
    }
    .nav-item.active {
        background: rgba(56,189,248,0.1);
        color: var(--accent-cyan);
        border-color: rgba(56,189,248,0.2);
    }
    .nav-icon { font-size: 1.1rem; width: 1.5rem; text-align: center; }

    /* ── Score ring ── */
    .score-ring {
        width: 56px; height: 56px;
        border-radius: 50%;
        background: conic-gradient(var(--accent-cyan) 0% var(--score-pct, 70%), var(--border) var(--score-pct, 70%) 100%);
        display: flex; align-items: center; justify-content: center;
        position: relative;
    }
    .score-ring::after {
        content: '';
        position: absolute;
        width: 44px; height: 44px;
        background: var(--bg-card);
        border-radius: 50%;
    }
    .score-value {
        position: relative; z-index: 1;
        font-family: 'Syne', sans-serif;
        font-size: 0.9rem;
        font-weight: 700;
        color: var(--accent-cyan);
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu, footer, header { visibility: hidden; }
    .viewerBadge_container__1QSob { display: none; }
    </style>
    """,
        unsafe_allow_html=True,
    )
