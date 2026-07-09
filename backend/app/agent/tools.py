"""
LangGraph agent tools for the AI-First CRM HCP module.

Five tools are implemented. The first two are the mandatory ones called
out in the assignment brief; the remaining three round out a realistic
sales-rep workflow.

  1. log_interaction   (MANDATORY) - captures + summarizes an HCP interaction
  2. schedule_followup  (MANDATORY) - books the rep's next touchpoint with the HCP
  3. analyze_sentiment              - classifies HCP sentiment during the visit
  4. check_compliance               - flags anything that looks off-label / non-compliant
  5. suggest_next_best_action       - LLM recommendation for what the rep should do next
"""

import json
import datetime as dt

from langchain_core.tools import tool

from app.agent.llm import primary_llm, context_llm


# ---------------------------------------------------------------------------
# 1. LOG INTERACTION  (mandatory)
# ---------------------------------------------------------------------------
@tool
def log_interaction(raw_text: str) -> str:
    """Capture a raw HCP interaction (from a structured form or free-text /
    chat transcript) and turn it into a clean structured record.

    Uses the LLM to:
      - write a 2-3 sentence summary of what was discussed
      - extract entities: products/drugs mentioned, topics discussed,
        samples or materials given, competitor mentions
    Returns a JSON string: {"summary": ..., "entities": {...}}
    """
    prompt = f"""You are a pharma CRM assistant. Read the field rep's notes
about a Healthcare Professional (HCP) interaction below and return ONLY
valid JSON (no markdown fences) with this exact shape:

{{
  "summary": "2-3 sentence neutral summary of the interaction",
  "entities": {{
    "products_discussed": ["..."],
    "topics": ["..."],
    "samples_given": ["..."],
    "competitor_mentions": ["..."]
  }}
}}

Interaction notes:
\"\"\"{raw_text}\"\"\"
"""
    response = primary_llm.invoke(prompt)
    try:
        return json.dumps(json.loads(response.content))
    except json.JSONDecodeError:
        # LLM occasionally wraps JSON in prose - fall back to a safe default
        return json.dumps({
            "summary": response.content[:300],
            "entities": {"products_discussed": [], "topics": [], "samples_given": [], "competitor_mentions": []},
        })


# ---------------------------------------------------------------------------
# 2. SCHEDULE FOLLOW-UP  (mandatory)
# ---------------------------------------------------------------------------
@tool
def schedule_followup(interaction_summary: str, requested_days: int = 14) -> str:
    """Given a summary of the interaction, decide when the rep should follow
    up with this HCP next, and produce a one-line reason.

    `requested_days` is a default cadence (e.g. 14 days) that the tool may
    shorten if the interaction signals urgency (e.g. HCP asked a question
    that needs an answer, or requested more samples).

    Returns JSON: {"followup_date": "YYYY-MM-DD", "reason": "..."}
    """
    prompt = f"""Based on this HCP interaction summary, should the sales rep
follow up sooner than the default {requested_days} days? Reply ONLY with
JSON: {{"days_from_now": <int>, "reason": "<one short sentence>"}}

Summary: \"\"\"{interaction_summary}\"\"\"
"""
    response = primary_llm.invoke(prompt)
    try:
        parsed = json.loads(response.content)
        days = int(parsed.get("days_from_now", requested_days))
        reason = parsed.get("reason", "Routine follow-up cadence.")
    except (json.JSONDecodeError, ValueError):
        days, reason = requested_days, "Routine follow-up cadence."

    followup_date = (dt.datetime.utcnow() + dt.timedelta(days=days)).date().isoformat()
    return json.dumps({"followup_date": followup_date, "reason": reason})


# ---------------------------------------------------------------------------
# 3. SENTIMENT ANALYSIS
# ---------------------------------------------------------------------------
@tool
def analyze_sentiment(raw_text: str) -> str:
    """Classify the HCP's overall sentiment/receptiveness during the
    interaction as one of: positive, neutral, negative.
    Returns JSON: {"sentiment": "...", "confidence": 0-1}
    """
    prompt = f"""Classify the HCP's sentiment/receptiveness in this
interaction as exactly one of: positive, neutral, negative.
Reply ONLY with JSON: {{"sentiment": "positive|neutral|negative", "confidence": <0-1 float>}}

Notes: \"\"\"{raw_text}\"\"\"
"""
    response = primary_llm.invoke(prompt)
    try:
        return json.dumps(json.loads(response.content))
    except json.JSONDecodeError:
        return json.dumps({"sentiment": "neutral", "confidence": 0.5})


# ---------------------------------------------------------------------------
# 4. COMPLIANCE CHECK
# ---------------------------------------------------------------------------
@tool
def check_compliance(raw_text: str) -> str:
    """Scan the interaction notes for anything that could be a pharma
    compliance risk: off-label promotion, unapproved claims, promised
    incentives, or promises about pricing/rebates.
    Returns JSON: {"flags": ["..."]}  (empty list if nothing found)
    """
    prompt = f"""You are a pharma compliance reviewer. Scan these HCP
interaction notes for potential compliance issues: off-label claims,
unapproved efficacy/safety claims, promised incentives or rebates, or
anything discouraged in pharma sales conduct.
Reply ONLY with JSON: {{"flags": ["short description of each issue found"]}}
Return {{"flags": []}} if nothing concerning is present.

Notes: \"\"\"{raw_text}\"\"\"
"""
    response = primary_llm.invoke(prompt)
    try:
        return json.dumps(json.loads(response.content))
    except json.JSONDecodeError:
        return json.dumps({"flags": []})


# ---------------------------------------------------------------------------
# 5. SUGGEST NEXT BEST ACTION
# ---------------------------------------------------------------------------
@tool
def suggest_next_best_action(interaction_summary: str, hcp_history: str = "") -> str:
    """Given the current interaction summary and (optionally) a short
    string describing the HCP's interaction history, recommend the single
    best next action for the rep (e.g. send a specific study, schedule a
    lunch-and-learn, loop in medical affairs).
    Returns JSON: {"next_best_action": "..."}
    """
    prompt = f"""You are an experienced pharma sales coach. Based on the
latest interaction summary and the HCP's history, recommend ONE concrete
next best action for the rep to take. Be specific and actionable.
Reply ONLY with JSON: {{"next_best_action": "<one sentence recommendation>"}}

Latest interaction: \"\"\"{interaction_summary}\"\"\"
HCP history: \"\"\"{hcp_history or "No prior history on file."}\"\"\"
"""
    response = context_llm.invoke(prompt)
    try:
        return json.dumps(json.loads(response.content))
    except json.JSONDecodeError:
        return json.dumps({"next_best_action": response.content[:200]})


ALL_TOOLS = [
    log_interaction,
    schedule_followup,
    analyze_sentiment,
    check_compliance,
    suggest_next_best_action,
]
