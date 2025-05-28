from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import DeliveryAgent
from schemas import DeliveryAgentCreate, DeliveryAgentUpdate, DeliveryAgentResponse, AgentStatusUpdate, AgentAssignment

router = APIRouter()

def get_db():
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=DeliveryAgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(agent: DeliveryAgentCreate, db: Session = Depends(get_db)):
    """Create a new delivery agent"""
    # Check if agent already exists
    db_agent = db.query(DeliveryAgent).filter(DeliveryAgent.email == agent.email).first()
    if db_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_agent = DeliveryAgent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("/{agent_id}", response_model=DeliveryAgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get delivery agent by ID"""
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found"
        )
    return agent

@router.get("/", response_model=List[DeliveryAgentResponse])
def get_agents(skip: int = 0, limit: int = 100, available_only: bool = False, db: Session = Depends(get_db)):
    """Get all delivery agents with pagination"""
    query = db.query(DeliveryAgent)
    
    if available_only:
        query = query.filter(DeliveryAgent.is_available == True)
    
    agents = query.offset(skip).limit(limit).all()
    return agents

@router.put("/{agent_id}", response_model=DeliveryAgentResponse)
def update_agent(agent_id: int, agent_update: DeliveryAgentUpdate, db: Session = Depends(get_db)):
    """Update delivery agent information"""
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found"
        )
    
    for field, value in agent_update.dict(exclude_unset=True).items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    return agent

@router.put("/{agent_id}/status", response_model=DeliveryAgentResponse)
def update_agent_status(agent_id: int, status_update: AgentStatusUpdate, db: Session = Depends(get_db)):
    """Update delivery agent availability status"""
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found"
        )
    
    agent.is_available = status_update.is_available
    if status_update.current_location:
        agent.current_location = status_update.current_location
    
    db.commit()
    db.refresh(agent)
    return agent

@router.put("/{agent_id}/assign", response_model=DeliveryAgentResponse)
def assign_agent_to_order(agent_id: int, assignment: AgentAssignment, db: Session = Depends(get_db)):
    """Assign delivery agent to an order"""
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found"
        )
    
    if not agent.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery agent is not available"
        )
    
    # Mark agent as unavailable
    agent.is_available = False
    db.commit()
    db.refresh(agent)
    
    return agent

@router.put("/{agent_id}/complete-delivery", response_model=DeliveryAgentResponse)
def complete_delivery(agent_id: int, db: Session = Depends(get_db)):
    """Mark delivery as complete and make agent available again"""
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found"
        )
    
    # Mark agent as available
    agent.is_available = True
    db.commit()
    db.refresh(agent)
    
    return agent

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Delete a delivery agent"""
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found"
        )
    
    db.delete(agent)
    db.commit()
    return None
