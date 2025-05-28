from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import httpx
import os
from dotenv import load_dotenv

from database import SessionLocal, engine
from models import Base
from routers import agents, deliveries
from schemas import DeliveryAgentResponse

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Delivery Agent Service",
    description="Food Delivery Agent Service API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(deliveries.router, prefix="/deliveries", tags=["deliveries"])

@app.get("/")
async def root():
    return {"message": "Delivery Agent Service is running"}

@app.get("/agents/available", response_model=List[DeliveryAgentResponse])
def get_available_agents(db: Session = Depends(get_db)):
    """Get all available delivery agents"""
    from models import DeliveryAgent
    agents = db.query(DeliveryAgent).filter(DeliveryAgent.is_available == True).all()
    return agents

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "delivery_agent_service"}
