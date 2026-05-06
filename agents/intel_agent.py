"""
agents/intel_agent.py
Competitive Intelligence Agent
Tested with: langchain==0.2.16, langchain-core==0.2.40, langchain-community==0.2.16
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from typing import Callable

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool

try:
    from langchain_community.tools.tavily_search import TavilySearchResults
    _HAS_TAVILY = True
except ImportError:
    _HAS_TAVILY = False

try:
    from langchain_community.utilities import SerpAPIWrapper
    _HAS_SERP = True
except ImportError:
    _HAS_SERP = False


# ── Prompts — kept SHORT to stay under 6000 TPM limit ────────────────────────

AGENT_PROMPT = PromptTemplate.from_template(
    """You are a competitive intelligence analyst. Research the competitor and return a JSON report.

Tools: {tools}
Tool names: {tool_names}

Task: {input}

Instructions:
- Use web_search 2-3 times maximum
- Gather: pricing, features, news, strengths, weaknesses
- Return ONLY valid JSON with these keys:
  company_name, founded, headquarters, funding, employee_count,
  core_products (list), pricing_tiers (list of {{name, price, description}}),
  strengths (list), weaknesses (list), opportunities (list), threats (list),
  recent_news (list of {{title, date, summary}}), market_positioning,
  tech_stack (list), target_customers, key_differentiators (list),
  threat_level (1-10 integer), overall_summary, sources (list)

{agent_scratchpad}"""
)


SYNTHESIS_PROMPT = """You are a strategy analyst. Analyze these competitors and return JSON.

Competitors: {raw_data}

Return ONLY valid JSON with keys:
- executive_summary (string)
- key_insights (list of 5 strings)
- threats_ranking (list of {{company, rationale}})
- whitespace_opportunities (list of 3 strings)
- recommended_actions (list of 5 strings)
- competitive_matrix (list of {{company, pricing_score, feature_score, market_score, tech_score, support_score, brand_score}})
- market_map (dict)
- methodology_note (string)

No markdown, no backticks, only JSON.
"""


def _build_executor(llm, tools):
    agent = create_react_agent(llm, tools, AGENT_PROMPT)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        max_iterations=3,          # reduced from 6 → fewer tokens per run
        handle_parsing_errors=True,
        return_intermediate_steps=False,
    )


class IntelAgent:

    def __init__(
        self,
        groq_key: str,
        tavily_key=None,
        serpapi_key=None,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.3,
        max_results: int = 3,      # reduced from 5 → shorter search results
        log_callback=None,
    ):
        self.groq_key     = groq_key
        self.tavily_key   = tavily_key
        self.serpapi_key  = serpapi_key
        self.model        = model
        self.temperature  = temperature
        self.max_results  = max_results
        self.log_callback = log_callback or (lambda msg, kind: None)

        self.llm   = self._build_llm()
        self.tools = self._build_tools()

    def _build_llm(self):
        return ChatGroq(
            api_key=self.groq_key,
            model_name=self.model,
            temperature=self.temperature,
            max_tokens=800,        # reduced from 1500 → stays under 6000 TPM
        )

    def _build_tools(self):
        tools = []

        if self.tavily_key and _HAS_TAVILY:
            import os
            os.environ["TAVILY_API_KEY"] = self.tavily_key
            try:
                tavily = TavilySearchResults(max_results=self.max_results)

                def _tavily_search(q, _t=tavily):
                    raw = str(_t.invoke(q))
                    # Truncate search result to 1500 chars to avoid 413
                    return raw[:1500] if len(raw) > 1500 else raw

                tools.append(Tool(
                    name="web_search",
                    func=lambda q: self._logged_tool("Tavily", q, lambda: _tavily_search(q)),
                    description="Search the web for company info. Input: search query string.",
                ))
                self.log_callback("Tavily search tool loaded", "result")
            except Exception as e:
                self.log_callback(f"Tavily setup failed: {e}", "warn")

        if self.serpapi_key and _HAS_SERP:
            import os
            os.environ["SERPAPI_API_KEY"] = self.serpapi_key
            try:
                serp = SerpAPIWrapper()

                def _serp_search(q, _s=serp):
                    raw = _s.run(q)
                    return raw[:1500] if len(raw) > 1500 else raw

                tools.append(Tool(
                    name="google_search",
                    func=lambda q: self._logged_tool("SerpAPI", q, lambda: _serp_search(q)),
                    description="Google search for company info. Input: search query string.",
                ))
                self.log_callback("SerpAPI search tool loaded", "result")
            except Exception as e:
                self.log_callback(f"SerpAPI setup failed: {e}", "warn")

        if not tools:
            tools.append(Tool(
                name="demo_search",
                func=self._demo_search,
                description="Returns demo data. Add API keys in Settings for live results.",
            ))
            self.log_callback(
                "No search API keys — running in DEMO mode. Add keys in Settings.", "warn"
            )

        return tools

    def _logged_tool(self, provider: str, query: str, fn: Callable) -> str:
        self.log_callback(f"[{provider}] Searching: {query}", "tool")
        start = time.time()
        try:
            result  = fn()
            elapsed = time.time() - start
            self.log_callback(
                f"[{provider}] Got {len(str(result))} chars in {elapsed:.1f}s", "result"
            )
            return str(result)
        except Exception as e:
            self.log_callback(f"[{provider}] Error: {e}", "warn")
            return f"Search failed: {e}"

    @staticmethod
    def _demo_search(query: str) -> str:
        return (
            f"Demo results for '{query}': Company founded 2010, SF. "
            "Tiers: Starter $29/mo, Pro $99/mo, Enterprise custom. "
            "Strengths: brand, market share. Weaknesses: expensive, complex. "
            "News: raised $50M Series C, launched AI features."
        )

    def research_competitor(self, company: str, your_company: str, focus_areas: list) -> dict:
        focus_str = ", ".join(focus_areas[:3]) if focus_areas else "pricing, features, news"
        query = (
            f"Research '{company}' competitor to '{your_company}'. "
            f"Focus: {focus_str}. Find pricing, strengths, weaknesses, recent news."
        )
        self.log_callback(f"Starting research on: {company}", "step")

        try:
            executor = _build_executor(self.llm, self.tools)

            try:
                result = executor.invoke({"input": query})

            except Exception as req_err:
                err_str = str(req_err)

                # 413 — request too large, try gemma2 which handles smaller context better
                if "413" in err_str:
                    self.log_callback(
                        "Request too large — switching to gemma2-9b-it", "warn"
                    )
                    self.model = "gemma2-9b-it"
                    self.llm   = self._build_llm()
                    executor   = _build_executor(self.llm, self.tools)
                    result     = executor.invoke({"input": query})

                # 429 — rate limit, switch to 8b
                elif "429" in err_str:
                    self.log_callback(
                        "Rate limit hit — switching to llama-3.1-8b-instant", "warn"
                    )
                    self.model = "llama-3.1-8b-instant"
                    self.llm   = self._build_llm()
                    executor   = _build_executor(self.llm, self.tools)
                    result     = executor.invoke({"input": query})

                else:
                    raise req_err

            raw_output = result.get("output", "{}")
            data       = self._extract_json(raw_output)

            if not data.get("company_name"):
                data["company_name"] = company
            data["researched_at"] = datetime.now().isoformat()
            data["your_company"]  = your_company

            self.log_callback(f"Completed research on {company}", "result")
            return data

        except Exception as e:
            self.log_callback(f"Error researching {company}: {e}", "error")
            return self._fallback_data(company, your_company, str(e))

    def synthesize_report(self, competitors_data: list, your_company: str, industry: str) -> dict:
        self.log_callback("Synthesizing cross-competitor analysis...", "step")

        # Trim competitor data to avoid 413 on synthesis
        trimmed = []
        for c in competitors_data:
            trimmed.append({
                "company_name":      c.get("company_name", ""),
                "threat_level":      c.get("threat_level", 5),
                "strengths":         c.get("strengths", [])[:3],
                "weaknesses":        c.get("weaknesses", [])[:3],
                "market_positioning":c.get("market_positioning", ""),
                "overall_summary":   c.get("overall_summary", "")[:300],
                "pricing_tiers":     c.get("pricing_tiers", [])[:2],
            })

        raw    = json.dumps(trimmed, indent=1)
        prompt = SYNTHESIS_PROMPT.format(raw_data=raw[:3000])  # hard cap at 3000 chars

        try:
            try:
                response = self.llm.invoke(prompt)
            except Exception as req_err:
                err_str = str(req_err)
                if "413" in err_str:
                    self.log_callback("Request too large in synthesis — switching to gemma2-9b-it", "warn")
                    self.model = "gemma2-9b-it"
                    self.llm   = self._build_llm()
                    response   = self.llm.invoke(prompt)
                elif "429" in err_str:
                    self.log_callback("Rate limit in synthesis — switching to llama-3.1-8b-instant", "warn")
                    self.model = "llama-3.1-8b-instant"
                    self.llm   = self._build_llm()
                    response   = self.llm.invoke(prompt)
                else:
                    raise req_err

            text      = response.content if hasattr(response, "content") else str(response)
            synthesis = self._extract_json(text)
            synthesis.update({
                "your_company":     your_company,
                "industry":         industry,
                "generated_at":     datetime.now().isoformat(),
                "competitor_count": len(competitors_data),
            })
            self.log_callback("Synthesis complete", "result")
            return synthesis

        except Exception as e:
            self.log_callback(f"Synthesis error: {e}", "error")
            return {
                "error":                    str(e),
                "generated_at":             datetime.now().isoformat(),
                "executive_summary":        f"Synthesis failed: {e}",
                "key_insights":             [],
                "recommended_actions":      [],
                "whitespace_opportunities": [],
                "threats_ranking":          [],
                "competitive_matrix":       [],
            }

    @staticmethod
    def _extract_json(text: str) -> dict:
        import re
        text = re.sub(r"```(?:json)?", "", text).strip().replace("```", "").strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                for m in re.finditer(r"\{[^{}]*\}", text):
                    try:
                        return json.loads(m.group())
                    except json.JSONDecodeError:
                        continue
        return {}

    @staticmethod
    def _fallback_data(company: str, your_company: str, error: str) -> dict:
        return {
            "company_name":       company,
            "your_company":       your_company,
            "error":              error,
            "overall_summary":    f"Research failed: {error}",
            "strengths":          [],
            "weaknesses":         [],
            "opportunities":      [],
            "threats":            [],
            "recent_news":        [],
            "pricing_tiers":      [],
            "core_products":      [],
            "threat_level":       5,
            "market_positioning": "Unknown — research failed",
            "researched_at":      datetime.now().isoformat(),
        }
