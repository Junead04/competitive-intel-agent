# ⚡ CompeteIQ — AI-Driven Competitive Intelligence Platform

> An enterprise-grade competitive intelligence agent powered by LangChain, Groq LLM, and Tavily/SerpAPI web search. Automatically researches competitors, synthesizes market trends, and generates actionable intelligence reports.

---

## 🗂️ Project Structure

```
competitive-intel-agent/
├── app.py                          # Main entry point
├── requirements.txt
├── .gitignore
├── .streamlit/
│   ├── config.toml                 # Streamlit theme & server config
│   └── secrets.toml.template       # API keys template (copy → secrets.toml)
│
├── agents/
│   └── intel_agent.py              # LangChain ReAct agent + Groq + Tavily
│
├── components/
│   ├── styles.py                   # Global CSS injection
│   └── sidebar.py                  # Sidebar navigation component
│
├── pages/
│   ├── dashboard.py                # Overview metrics & threat map
│   ├── research.py                 # Research configuration + agent runner
│   ├── reports.py                  # Report viewer, comparison, export
│   └── settings.py                 # API keys & preferences
│
└── utils/
    └── session.py                  # Streamlit session state management
```

---

## 🚀 Setup — Step by Step

### Step 1 — Clone / Download

```bash
git clone https://github.com/yourusername/competitive-intel-agent
cd competitive-intel-agent
```

Or just unzip the project folder.

### Step 2 — Create Virtual Environment

```bash
python -m venv venv

# Activate:
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Get Free API Keys

| Service | URL | Free Tier |
|---------|-----|-----------|
| **Groq** (LLM) | https://console.groq.com | 14,400 req/day |
| **Tavily** (search) | https://tavily.com | 1,000 searches/month |
| **SerpAPI** (optional) | https://serpapi.com | 100 searches/month |

### Step 5 — Configure API Keys

**Option A — Streamlit secrets (recommended for local + cloud):**

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit secrets.toml and add your keys
```

```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "gsk_your_actual_key"
TAVILY_API_KEY = "tvly-your_actual_key"
SERPAPI_KEY = ""   # optional
```

**Option B — Environment variables:**

```bash
export GROQ_API_KEY="gsk_..."
export TAVILY_API_KEY="tvly-..."
```

**Option C — In-app UI:**

Leave keys empty and enter them in the **Settings** page when the app runs.

### Step 6 — Run Locally

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🌐 Deploy to Streamlit Cloud (Free)

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/competitive-intel-agent.git
git push -u origin main
```

> ⚠️ Make sure `.streamlit/secrets.toml` is in your `.gitignore` — never commit API keys.

### Step 2 — Connect to Streamlit Cloud

1. Go to **https://share.streamlit.io**
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository, branch `main`, and main file `app.py`
5. Click **"Deploy!"**

### Step 3 — Add Secrets in Streamlit Cloud

1. In your deployed app, click **⋮ → Settings → Secrets**
2. Paste your secrets in TOML format:

```toml
GROQ_API_KEY = "gsk_your_actual_key"
TAVILY_API_KEY = "tvly-your_actual_key"
SERPAPI_KEY = ""
```

3. Click **Save** — the app will restart with your keys loaded.

---

## 🔧 How It Works

### Architecture

```
User Input (company + competitors)
        ↓
Research Page (configure + launch)
        ↓
IntelAgent (LangChain ReAct loop)
    ├── web_search tool (Tavily)
    ├── google_search tool (SerpAPI)
    └── LLM reasoning (Groq/Llama3)
        ↓
Per-competitor structured JSON
        ↓
Synthesis (cross-competitor analysis)
        ↓
Report stored in session state
        ↓
Dashboard / Reports / Export
```

### Agent Flow (ReAct Pattern)

1. **Thought** — LLM reasons about what to search next
2. **Action** — Calls `web_search` or `google_search` tool
3. **Observation** — Gets search results back
4. **Repeat** — Up to `max_iterations` times
5. **Final Answer** — Outputs structured JSON

### Pages

| Page | Function |
|------|----------|
| **Dashboard** | KPI metrics, recent reports, threat heatmap |
| **Research** | Configure + run agent, live log, results |
| **Reports** | Browse history, compare, export JSON/CSV/MD |
| **Settings** | API keys, model config, research defaults |

---

## ⚡ Additional Features (beyond base spec)

- **Multi-competitor parallel research** with progress tracking
- **Cross-competitor synthesis** with strategic insights
- **Threat ranking & scoring** (1–10 scale per competitor)
- **SWOT analysis** per competitor (Strengths, Weaknesses, Opportunities, Threats)
- **Pricing tier extraction** per competitor
- **Recent news tracking** per competitor
- **Competitive matrix** comparison table
- **Market whitespace** opportunity identification
- **Export** to JSON, Markdown, CSV
- **Agent activity log** with live streaming
- **API status indicators** in sidebar
- **Session statistics** (reports, searches, competitors tracked)
- **Groq connection tester** in Settings
- **Enterprise dark UI** with custom design system

---

## 🛠️ Customization

### Change the LLM model

In `Settings → Model`, pick from:
- `llama3-70b-8192` — Best quality
- `llama3-8b-8192` — Fastest
- `mixtral-8x7b-32768` — Largest context

Or edit `utils/session.py` to change the default.

### Add custom focus areas

Edit `pages/research.py` → `focus_options` list.

### Modify the research prompt

Edit `agents/intel_agent.py` → `AGENT_PROMPT` or `SYNTHESIS_PROMPT`.

### Add more tools to the agent

```python
# In agents/intel_agent.py → _build_tools()
tools.append(Tool(
    name="my_tool",
    func=my_function,
    description="What this tool does and when to use it.",
))
```

---

## 🔒 Security Notes

- API keys are stored only in Streamlit session memory (browser session)
- Use `secrets.toml` for persistent key storage — it's never served to clients
- Never commit `secrets.toml` to git
- All external calls go through official API SDKs

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit + Custom CSS |
| LLM | Groq (Llama 3 70B) |
| Agent | LangChain ReAct |
| Search | Tavily / SerpAPI |
| Data | Python dicts + session state |
| Deploy | Streamlit Cloud (free) |

---

## 📄 License

MIT — free for personal and commercial use.
