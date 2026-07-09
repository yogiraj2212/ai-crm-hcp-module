"""
Builds the LangGraph agent that manages HCP interactions.

The agent is a ReAct-style graph: the LLM (context_llm, since it needs to
reason across a multi-turn chat) decides which of the 5 tools to call and
in what order, then produces a final natural-language reply plus a
structured "draft interaction" once it has enough information to log one.
"""

import json

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from app.agent.llm import context_llm
from app.agent.tools import ALL_TOOLS

SYSTEM_PROMPT = """You are the AI assistant embedded in a pharma CRM's
"Log Interaction" screen. A field sales rep is telling you, in a
conversational chat, about a visit they just had with a Healthcare
Professional (HCP).

Your job:
1. Ask clarifying questions if key details are missing (which HCP, what
   was discussed, samples given, HCP reaction) - keep it to one short
   question at a time.
2. Once you have enough detail, call ALL FIVE of your tools in this same
   turn: log_interaction, analyze_sentiment, check_compliance,
   schedule_followup, and suggest_next_best_action. Pass the full visit
   description as raw_text / interaction_summary to each as appropriate.
3. Reply to the rep in plain, friendly language summarizing what you
   logged - never dump raw JSON at the user.

You have five tools available: log_interaction, schedule_followup,
analyze_sentiment, check_compliance, suggest_next_best_action.
"""

# Pre-built ReAct agent: LLM + tools + a checkpointer-free loop.
# LangGraph handles the tool-calling loop (LLM -> tool -> LLM -> ...) for us.
hcp_agent = create_react_agent(context_llm, ALL_TOOLS)


def _extract_tool_results(messages: list) -> dict:
    """Pull out each tool's JSON output from the agent's message trace,
    keyed by tool name. If a tool was called more than once, the last
    call wins."""
    results = {}
    for msg in messages:
        if isinstance(msg, ToolMessage):
            try:
                results[msg.name] = json.loads(msg.content)
            except (json.JSONDecodeError, TypeError):
                results[msg.name] = None
    return results


def run_agent_turn(user_message: str, history: list[dict] | None = None) -> dict:
    """Run one turn of the conversational Log Interaction chat.

    `history` is a list of {"role": "user"|"assistant", "content": str}
    dicts sent by the frontend so the graph is stateless between HTTP
    requests (simplest option for a take-home assignment; swap in
    LangGraph's checkpointer + a thread_id for production persistence).

    Returns a "draft_interaction" dict (ready to persist) once the agent
    has actually called log_interaction this turn - i.e. once it decided
    it had enough information to log the visit.
    """
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for turn in (history or []):
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=user_message))

    result = hcp_agent.invoke({"messages": messages})
    final_message = result["messages"][-1]

    new_history = (history or []) + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": final_message.content},
    ]

    tool_results = _extract_tool_results(result["messages"])

    draft_interaction = None
    ready_to_log = bool(tool_results.get("log_interaction"))

    if ready_to_log:
        log_result = tool_results.get("log_interaction") or {}
        sentiment_result = tool_results.get("analyze_sentiment") or {}
        compliance_result = tool_results.get("check_compliance") or {}
        followup_result = tool_results.get("schedule_followup") or {}
        nba_result = tool_results.get("suggest_next_best_action") or {}

        draft_interaction = {
            "summary": log_result.get("summary"),
            "entities": log_result.get("entities"),
            "sentiment": sentiment_result.get("sentiment"),
            "compliance_flags": compliance_result.get("flags", []),
            "next_best_action": nba_result.get("next_best_action"),
            "followup_date": followup_result.get("followup_date"),
        }

    return {
        "reply": final_message.content,
        "history": new_history,
        "ready_to_log": ready_to_log,
        "draft_interaction": draft_interaction,
    }
