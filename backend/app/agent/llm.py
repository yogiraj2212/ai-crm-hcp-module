from langchain_groq import ChatGroq

from app.config import settings

# Fast, cheap model for most tool-level calls (extraction, classification)
primary_llm = ChatGroq(
    model=settings.PRIMARY_MODEL,       # gemma2-9b-it
    api_key=settings.GROQ_API_KEY,
    temperature=0.2,
)

# Larger-context model for anything that needs more reasoning
# (multi-turn chat, next-best-action suggestions)
context_llm = ChatGroq(
    model=settings.CONTEXT_MODEL,       # llama-3.3-70b-versatile
    api_key=settings.GROQ_API_KEY,
    temperature=0.4,
)
