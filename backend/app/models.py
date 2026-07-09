import uuid
import datetime as dt

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class HCP(Base):
    """A Healthcare Professional (doctor/pharmacist) tracked in the CRM."""

    __tablename__ = "hcps"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255))
    hospital = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    interactions = relationship("Interaction", back_populates="hcp")


class Interaction(Base):
    """A single logged interaction between a sales rep and an HCP."""

    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    hcp_id = Column(String(36), ForeignKey("hcps.id"), nullable=False)
    rep_id = Column(String(36), nullable=False)  # sales rep user id

    # raw input, either the structured form payload or the free-text chat transcript
    input_mode = Column(Enum("form", "chat", name="input_mode_enum"), default="form")
    raw_text = Column(Text)  # free-text notes / chat transcript
    structured_payload = Column(JSON)  # data submitted via the structured form

    # fields populated by the LangGraph agent
    summary = Column(Text)
    entities = Column(JSON)  # {"topics": [...], "samples_given": [...], "products_discussed": [...]}
    sentiment = Column(String(20))  # positive / neutral / negative
    compliance_flags = Column(JSON)  # list of compliance warnings, if any
    next_best_action = Column(Text)
    followup_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=dt.datetime.utcnow)

    hcp = relationship("HCP", back_populates="interactions")
