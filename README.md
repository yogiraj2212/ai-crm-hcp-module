# AI-First CRM — HCP Module: Log Interaction Screen

An AI-first "Log Interaction" screen for a pharma CRM's Healthcare
Professional (HCP) module. Field sales reps can log a visit either through
a **structured form** or a **conversational chat interface**, and a
LangGraph agent handles the AI side: summarization, entity extraction,
sentiment, compliance flags, follow-up scheduling, and next-best-action.

## Tech stack

| Layer          | Choice                                   |
|----------------|-------------------------------------------|
| Frontend       | React + Redux (Redux Toolkit)             |
| Backend        | Python, FastAPI                           |
| AI agent       | LangGraph (ReAct-style agent)             |
| LLMs           | Groq — `gemma2-9b-it` (tool calls), `llama-3.3-70b-versatile` (chat/reasoning) |
| Database       | MySQL (SQLAlchemy ORM + PyMySQL driver)   |
| Font           | Google Inter                              |

## Architecture at a glance

```
frontend (React/Redux)
   │  toggle: Structured Form  |  Chat
   ▼
FastAPI backend
   ├── /api/interactions/form   → runs all 5 tools once, saves record
   ├── /api/interactions/chat   → LangGraph agent decides which tools to call, turn by turn
   └── /api/interactions/{hcp}  → history
   ▼
LangGraph agent (app/agent/graph.py)
   ├── log_interaction        (MANDATORY) — LLM summary + entity extraction
   ├── schedule_followup      (MANDATORY) — decides next follow-up date
   ├── analyze_sentiment      — positive / neutral / negative
   ├── check_compliance       — flags off-label / risky language
   └── suggest_next_best_action — recommends the rep's next move
   ▼
MySQL (hcps, interactions tables)
```

**Note on the two mandatory tools:** the assignment doc named `Log
Interaction` as one mandatory tool and was cut off before naming the
second. This build assumes **`Schedule Follow-up`** as the second
mandatory tool, since it's the natural companion action after logging a
visit — swap it out if your actual brief specifies something else.

## Why these choices

- **Two entry paths, one pipeline.** The structured form and the chat both
  ultimately produce a `raw_text` payload that goes through the same 5
  tools, so a rep gets identical AI-derived insights (summary, sentiment,
  compliance, follow-up, next-best-action) no matter which mode they use.
- **create_react_agent for chat.** For the multi-turn chat, LangGraph's
  prebuilt ReAct agent lets the LLM decide, turn by turn, when it has
  enough information to call `log_interaction` vs. when it should ask a
  clarifying question first — closer to how a rep would actually want to
  talk to it.
- **Stateless chat history.** The frontend re-sends the running chat
  history each turn rather than relying on server-side session state —
  simplest option for this assignment's scope. For production, swap in
  LangGraph's checkpointer with a `thread_id` per HCP visit.
- **Groq split by task.** `gemma2-9b-it` is fast/cheap and used for the
  single-shot tool calls (extraction, classification). The larger
  `llama-3.3-70b-versatile` is reserved for the conversational agent and
  next-best-action, where more reasoning helps.

## Running it locally

### 1. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env: set GROQ_API_KEY and DATABASE_URL

# make sure MySQL is running and the DB in DATABASE_URL exists, e.g.:
#   mysql -u root -p -e "CREATE DATABASE hcp_crm;"

uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000` (docs at `/docs`).

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:3000` and calls the backend at
`http://localhost:8000` (override with `REACT_APP_API_URL`).

### 3. Try it

- **Structured Form tab:** fill in interaction type, products discussed,
  samples given, notes → "Log interaction" → see summary, sentiment,
  compliance flags, follow-up date, and next-best-action appear below.
- **Chat tab:** type something like *"Just met Dr. Rao, discussed
  Cardovex, she wants more efficacy data and asked about pricing"* and the
  agent will respond, ask clarifying questions if needed, and log the
  interaction using the same tools behind the scenes.

## Project structure

```
hcp-crm/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + CORS
│   │   ├── config.py          # env-based settings
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models.py          # HCP, Interaction ORM models
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── agent/
│   │   │   ├── llm.py         # Groq LLM clients
│   │   │   ├── tools.py       # the 5 LangGraph tools
│   │   │   └── graph.py       # ReAct agent wiring for the chat path
│   │   └── routers/
│   │       └── interactions.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── store.js
    │   ├── api.js
    │   ├── slices/interactionSlice.js
    │   └── components/
    │       ├── LogInteractionScreen.jsx  # form/chat toggle
    │       ├── StructuredForm.jsx
    │       └── ChatInterface.jsx
    └── package.json
```

## What's stubbed vs. what's real

This is a take-home-assignment-scoped build, so a few things are
intentionally simplified — called out here rather than hidden:

- **Auth:** `rep_id` / `hcp_id` are hardcoded in `App.jsx` instead of coming
  from a login flow or HCP directory search.
- **Chat persistence:** history is passed frontend → backend → frontend each
  turn rather than stored server-side mid-conversation (see note above on
  LangGraph checkpointers).
- **Chat → DB save:** once the agent calls `log_interaction` in a turn (meaning
  it decided it has enough information), the backend collects that turn's
  tool outputs and saves a row to the same `interactions` table the
  structured form uses. The frontend shows the same "Logged & analyzed"
  result card in both tabs.

## For the video walkthrough

Suggested flow to hit all four points from the brief:
1. Open the app, show the Structured Form path end-to-end.
2. Switch to Chat, describe a visit conversationally, show the agent asking
   a follow-up question and then logging it.
3. Open `backend/app/agent/tools.py` and walk through the 5 tools.
4. Open `backend/app/agent/graph.py` and explain the ReAct loop.
5. Close with a 30-second summary of what the task was asking for and how
   this maps to it.
