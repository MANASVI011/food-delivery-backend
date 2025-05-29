from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import httpx
import os
from datetime import datetime

from database import get_db
from models import DeliveryAgent, Delivery
from schemas import DeliveryCreate, DeliveryResponse, DeliveryStatusUpdate

router = APIRouter()

@router.post("/", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db)):
    """Create a new delivery record"""
    # Verify delivery agent exists
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == delivery.delivery_agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found"
        )
    
    # Check if delivery already exists for this order
    existing_delivery = db.query(Delivery).filter(Delivery.order_id == delivery.order_id).first()
    if existing_delivery:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery already exists for this order"
        )
    
    db_delivery = Delivery(**delivery.dict())
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery

@router.get("/{order_id}", response_model=DeliveryResponse)
def get_delivery_by_order(order_id: int, db: Session = Depends(get_db)):
    """Get delivery information by order ID"""
    delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found for this order"
        )
    return delivery

@router.get("/agent/{agent_id}", response_model=List[DeliveryResponse])
def get_agent_deliveries(agent_id: int, status_filter: str = None, db: Session = Depends(get_db)):
    """Get all deliveries for a specific agent"""
    # Verify agent exists
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found"
        )
    
    query = db.query(Delivery).filter(Delivery.delivery_agent_id == agent_id)
    
    if status_filter:
        query = query.filter(Delivery.status == status_filter)
    
    deliveries = query.order_by(Delivery.created_at.desc()).all()
    return deliveries

@router.put("/{order_id}/status", response_model=DeliveryResponse)
async def update_delivery_status(order_id: int, status_update: DeliveryStatusUpdate, db: Session = Depends(get_db)):
    """Update delivery status"""
    delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found for this order"
        )
    
    valid_statuses = ["assigned", "picked_up", "in_transit", "delivered", "failed"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Business logic for status transitions
    current_status = delivery.status
    new_status = status_update.status
    
    # Define valid status transitions
    valid_transitions = {
        "assigned": ["picked_up", "failed"],
        "picked_up": ["in_transit", "failed"],
        "in_transit": ["delivered", "failed"],
        "delivered": [],  # Final state
        "failed": []      # Final state
    }
    
    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {current_status} to {new_status}"
        )
    
    # Update delivery status
    delivery.status = new_status
    if status_update.notes:
        delivery.notes = status_update.notes
    
    # Set timestamps based on status
    if new_status == "picked_up":
        delivery.pickup_time = datetime.now()
    elif new_status == "delivered":
        delivery.delivery_time = datetime.now()
        # Make agent available again
        agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == delivery.delivery_agent_id).first()
        if agent:
            agent.is_available = True
    elif new_status == "failed":
        # Make agent available again
        agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == delivery.delivery_agent_id).first()
        if agent:
            agent.is_available = True
    
    db.commit()
    db.refresh(delivery)
    
    # Notify other services about status change
    await notify_delivery_status_change(order_id, new_status)
    
    return delivery

@router.post("/{order_id}/ready")
async def mark_order_ready_for_pickup(order_id: int, db: Session = Depends(get_db)):
    """Mark order as ready for pickup (called by restaurant service)"""
    delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
    
    if not delivery:
        # Create delivery record if it doesn't exist
        # This might happen if the order was assigned but delivery record wasn't created
        return {"message": "Order noted as ready, delivery record will be created when agent is assigned"}
    
    # Notify the assigned agent (in a real system, this would be push notification, SMS, etc.)
    return {"message": f"Delivery agent {delivery.delivery_agent_id} notified that order {order_id} is ready for pickup"}

@router.get("/", response_model=List[DeliveryResponse])
def get_all_deliveries(skip: int = 0, limit: int = 100, status_filter: str = None, db: Session = Depends(get_db)):
    """Get all deliveries with pagination"""
    query = db.query(Delivery)
    
    if status_filter:
        query = query.filter(Delivery.status == status_filter)
    
    deliveries = query.order_by(Delivery.created_at.desc()).offset(skip).limit(limit).all()
    return deliveries

async def notify_delivery_status_change(order_id: int, status: str):
    """Notify other services about delivery status changes"""
    user_service_url = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
    restaurant_service_url = os.getenv("RESTAURANT_SERVICE_URL", "http://localhost:8002")
    
    try:
        async with httpx.AsyncClient() as client:
            # Notify user service
            await client.post(
                f"{user_service_url}/orders/{order_id}/delivery-status-update",
                json={"delivery_status": status}
            )
            
            # Notify restaurant service
            await client.post(
                f"{restaurant_service_url}/orders/{order_id}/delivery-status-update",
                json={"delivery_status": status}
            )
    
    except httpx.RequestError:
        # Log error but don't fail the main operation
        pass
