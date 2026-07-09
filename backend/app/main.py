from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app.routers import interactions
from app import models

Base.metadata.create_all(bind=engine)


def seed_demo_data():
    """Insert a demo HCP row matching the frontend's hardcoded hcp_id,
    so a fresh install works out of the box without a manual INSERT."""
    db = SessionLocal()
    try:
        existing = db.get(models.HCP, "hcp-001")
        if not existing:
            db.add(models.HCP(
                id="hcp-001",
                name="Dr. Anjali Rao",
                specialty="Cardiology",
                hospital="City General Hospital",
                email="anjali.rao@example.com",
                phone="9876543210",
            ))
            db.commit()
    finally:
        db.close()


seed_demo_data()

app = FastAPI(title="AI-First CRM - HCP Module")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interactions.router)


@app.get("/health")
def health():
    return {"status": "ok"}
