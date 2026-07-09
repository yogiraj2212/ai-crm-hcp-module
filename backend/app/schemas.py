import datetime as dt
from typing import Optional, Any, List

from pydantic import BaseModel


class InteractionCreate(BaseModel):
    hcp_id: str
    rep_id: str
    input_mode: str = "form"          # "form" | "chat"
    raw_text: Optional[str] = None    # free text / chat transcript
    structured_payload: Optional[dict] = None  # structured form fields


class InteractionOut(BaseModel):
    id: str
    hcp_id: str
    rep_id: str
    input_mode: str
    raw_text: Optional[str]
    structured_payload: Optional[dict]
    summary: Optional[str]
    entities: Optional[dict]
    sentiment: Optional[str]
    compliance_flags: Optional[List[str]]
    next_best_action: Optional[str]
    followup_date: Optional[dt.datetime]
    created_at: dt.datetime

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    hcp_id: str
    rep_id: str
    message: str
    # running chat history the frontend keeps and re-sends each turn
    history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    reply: str
    history: List[dict]
    # populated once the agent decides enough info has been gathered to log
    ready_to_log: bool = False
    draft_interaction: Optional[dict] = None
    saved_interaction_id: Optional[str] = None
