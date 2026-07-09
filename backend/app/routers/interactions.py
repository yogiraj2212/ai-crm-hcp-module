import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.agent.tools import (
    log_interaction,
    schedule_followup,
    analyze_sentiment,
    check_compliance,
    suggest_next_best_action,
)
from app.agent.graph import run_agent_turn

router = APIRouter(prefix="/api/interactions", tags=["interactions"])


@router.post("/form", response_model=schemas.InteractionOut)
def log_via_form(payload: schemas.InteractionCreate, db: Session = Depends(get_db)):
    """Structured-form path: rep fills out fields directly, we still run the
    interaction through the same 5 tools so form and chat produce identical
    downstream data quality."""

    raw_text = payload.raw_text or json.dumps(payload.structured_payload or {})

    log_result = json.loads(log_interaction.invoke({"raw_text": raw_text}))
    sentiment_result = json.loads(analyze_sentiment.invoke({"raw_text": raw_text}))
    compliance_result = json.loads(check_compliance.invoke({"raw_text": raw_text}))
    followup_result = json.loads(
        schedule_followup.invoke({"interaction_summary": log_result["summary"]})
    )
    nba_result = json.loads(
        suggest_next_best_action.invoke({"interaction_summary": log_result["summary"]})
    )

    interaction = models.Interaction(
        hcp_id=payload.hcp_id,
        rep_id=payload.rep_id,
        input_mode=payload.input_mode,
        raw_text=raw_text,
        structured_payload=payload.structured_payload,
        summary=log_result["summary"],
        entities=log_result["entities"],
        sentiment=sentiment_result["sentiment"],
        compliance_flags=compliance_result["flags"],
        next_best_action=nba_result["next_best_action"],
        followup_date=followup_result["followup_date"],
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@router.post("/chat", response_model=schemas.ChatResponse)
def chat_turn(payload: schemas.ChatMessage, db: Session = Depends(get_db)):
    """Conversational path: the LangGraph agent decides when/which tools to
    call as the rep describes the visit in free-form chat. Once the agent
    has actually logged the interaction (called log_interaction this
    turn), we persist it to the same `interactions` table the structured
    form uses."""
    result = run_agent_turn(payload.message, payload.history)

    saved_id = None
    if result["ready_to_log"] and result["draft_interaction"]:
        draft = result["draft_interaction"]
        interaction = models.Interaction(
            hcp_id=payload.hcp_id,
            rep_id=payload.rep_id,
            input_mode="chat",
            raw_text=payload.message,
            structured_payload=None,
            summary=draft.get("summary"),
            entities=draft.get("entities"),
            sentiment=draft.get("sentiment"),
            compliance_flags=draft.get("compliance_flags"),
            next_best_action=draft.get("next_best_action"),
            followup_date=draft.get("followup_date"),
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        saved_id = interaction.id

    return schemas.ChatResponse(
        reply=result["reply"],
        history=result["history"],
        ready_to_log=result["ready_to_log"],
        draft_interaction=result["draft_interaction"],
        saved_interaction_id=saved_id,
    )


@router.get("/{hcp_id}", response_model=list[schemas.InteractionOut])
def list_interactions_for_hcp(hcp_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.Interaction)
        .filter(models.Interaction.hcp_id == hcp_id)
        .order_by(models.Interaction.created_at.desc())
        .all()
    )
