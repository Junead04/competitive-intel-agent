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

# ── Imports — pinned to langchain 0.2.x ──────────────────────────────────────
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


# ── ReAct Prompt ─────────────────────────────────────────────────────────────

AGENT_PROMPT = PromptTemplate.from_template(
    """You are CompeteIQ, an elite competitive intelligence analyst AI.
Your task is to deeply research competitors and synthesize actionable market intelligence.

## Available Tools
{tools}

## Tool Names
{tool_names}

## Research Objective
{input}

## Instructions
1. Use search tools to gather current data about the competitor
2. Search for: pricing, features, recent news, funding, customer reviews, positioning
3. Look for weaknesses, opportunities, and strategic threats
4. Think step-by-step and be thorough
5. Output ONLY a valid JSON object as your Final Answer

Output your FINAL answer as a valid JSON object with these exact keys:
- company_name (string)
- founded (string)
- headquarters (string)
- funding (string)
- employee_count (string)
- core_products (list of strings)
- pricing_tiers (list of dicts with keys: name, price, description)
- strengths (list of strings)
- weaknesses (list of strings)
- opportunities (list of strings)
- threats (list of strings)
- recent_news (list of dicts with keys: title, date, summary)
- market_positioning (string)
- tech_stack (list of strings)
- target_customers (string)
- key_differentiators (list of strings)
- threat_level (integer 1-10)
- overall_summary (string, 2-3 paragraphs)
- sources (list of URL strings)

{agent_scratchpad}"""
)


SYNTHESIS_PROMPT = """You are a senior strategy analyst.
Given the following raw competitive intelligence data for multiple companies,
produce a comprehensive comparative analysis report in JSON format with these exact keys:

- executive_summary: 3-4 paragraph strategic overview (string)
- market_map: dict mapping company name to market segment
- competitive_matrix: list of dicts, each with keys:
  company, pricing_score, feature_score, market_score, tech_score, support_score, brand_score
  (all scores are integers 1-10)
- key_insights: list of 5-7 actionable strategic insight strings
- threats_ranking: list of dicts with keys: company, rationale
  sorted from highest to lowest threat
- whitespace_opportunities: list of market gap/opportunity strings
- recommended_actions: list of 5 strategic recommendation strings
- methodology_note: string describing data sources used

Raw competitor data:
{raw_data}

Return ONLY valid JSON. No markdown, no backticks, no explanation outside the JSON.
"""


# ── Main Agent Class ──────────────────────────────────────────────────────────

class IntelAgent:
    """LangChain ReAct agent for competitive intelligence research."""

    def __init__(
        self,
        groq_key: str,
        tavily_key=None,
        serpapi_key=None,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.3,
        max_results: int = 5,
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
            max_tokens=4096,
        )

    def _build_tools(self):
        tools = []

        # Tavily (preferred)
        if self.tavily_key and _HAS_TAVILY:
            import os
            os.environ["TAVILY_API_KEY"] = self.tavily_key
            try:
                tavily = TavilySearchResults(max_results=self.max_results)
                tools.append(Tool(
                    name="web_search",
                    func=lambda q, _t=tavily: self._logged_tool(
                        "Tavily", q, lambda: str(_t.invoke(q))
                    ),
                    description=(
                        "Search the live web for current info about companies, "
                        "pricing, news, and market data. Input: a search query string."
                    ),
                ))
                self.log_callback("Tavily search tool loaded", "result")
            except Exception as e:
                self.log_callback(f"Tavily setup failed: {e}", "warn")

        # SerpAPI (fallback)
        if self.serpapi_key and _HAS_SERP:
            import os
            os.environ["SERPAPI_API_KEY"] = self.serpapi_key
            try:
                serp = SerpAPIWrapper()
                tools.append(Tool(
                    name="google_search",
                    func=lambda q, _s=serp: self._logged_tool(
                        "SerpAPI", q, lambda: _s.run(q)
                    ),
                    description=(
                        "Google search for company info, funding rounds, "
                        "product launches. Input: search query string."
                    ),
                ))
                self.log_callback("SerpAPI search tool loaded", "result")
            except Exception as e:
                self.log_callback(f"SerpAPI setup failed: {e}", "warn")

        # Demo fallback
        if not tools:
            tools.append(Tool(
                name="demo_search",
                func=self._demo_search,
                description=(
                    "Returns demo data. Add TAVILY_API_KEY in Settings for live results."
                ),
            ))
            self.log_callback(
                "No search API keys — running in DEMO mode. Add keys in Settings.",
                "warn",
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
            "3 pricing tiers: Starter $29/mo, Pro $99/mo, Enterprise custom. "
            "Strengths: brand, market share. Weaknesses: expensive, complex. "
            "News: raised $50M Series C, launched AI features. "
            "Add real API keys in Settings for live data."
        )

    def research_competitor(self, company: str, your_company: str, focus_areas: list) -> dict:
        focus_str = ", ".join(focus_areas) if focus_areas else "all areas"
        query = (
            f"Research '{company}' as a competitor to '{your_company}'. "
            f"Focus: {focus_str}. "
            f"Find pricing, features, recent news, funding, strengths, weaknesses."
        )
        self.log_callback(f"Starting research on: {company}", "step")

        try:
            agent    = create_react_agent(self.llm, self.tools, AGENT_PROMPT)
            executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=False,
                max_iterations=8,
                handle_parsing_errors=True,
                return_intermediate_steps=False,
            )
            result     = executor.invoke({"input": query})
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
        raw    = json.dumps(competitors_data, indent=2)
        prompt = SYNTHESIS_PROMPT.format(raw_data=raw[:12000])
        try:
            response  = self.llm.invoke(prompt)
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
