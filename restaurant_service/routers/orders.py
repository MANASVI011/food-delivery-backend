from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import httpx
import os
from datetime import datetime, timedelta

from database import get_db
from models import Restaurant, Order, DeliveryAgent
from schemas import OrderResponse, OrderStatusUpdate, DeliveryAgentAssignment

router = APIRouter()

@router.get("/restaurant/{restaurant_id}", response_model=List[OrderResponse])
def get_restaurant_orders(restaurant_id: int, status_filter: str = None, db: Session = Depends(get_db)):
    """Get all orders for a restaurant"""
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    query = db.query(Order).filter(Order.restaurant_id == restaurant_id)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    orders = query.order_by(Order.created_at.desc()).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: int, status_update: OrderStatusUpdate, db: Session = Depends(get_db)):
    """Update order status (accept/reject/prepare/ready)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    valid_statuses = ["pending", "accepted", "rejected", "preparing", "ready", "picked_up", "delivered", "cancelled"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Business logic for status transitions
    current_status = order.status
    new_status = status_update.status
    
    # Define valid status transitions
    valid_transitions = {
        "pending": ["accepted", "rejected"],
        "accepted": ["preparing", "cancelled"],
        "preparing": ["ready", "cancelled"],
        "ready": ["picked_up", "cancelled"],
        "picked_up": ["delivered"],
        "delivered": [],  # Final state
        "rejected": [],   # Final state
        "cancelled": []   # Final state
    }
    
    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {current_status} to {new_status}"
        )
    
    order.status = new_status
    
    # Auto-assign delivery agent when order is ready
    if new_status == "ready" and not order.delivery_agent_id:
        await assign_delivery_agent(order_id, db)
    
    db.commit()
    db.refresh(order)
    
    # Notify other services about status change
    await notify_status_change(order_id, new_status)
    
    return order

@router.post("/{order_id}/assign-agent", response_model=OrderResponse)
async def assign_delivery_agent_manual(order_id: int, assignment: DeliveryAgentAssignment, db: Session = Depends(get_db)):
    """Manually assign a delivery agent to an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify delivery agent exists and is available
    delivery_service_url = os.getenv("DELIVERY_SERVICE_URL", "http://localhost:8003")
    
    try:
        async with httpx.AsyncClient() as client:
            agent_response = await client.get(
                f"{delivery_service_url}/agents/{assignment.delivery_agent_id}"
            )
            if agent_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Delivery agent not found"
                )
            
            agent_data = agent_response.json()
            if not agent_data.get("is_available"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Delivery agent is not available"
                )
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to delivery service"
        )
    
    order.delivery_agent_id = assignment.delivery_agent_id
    if assignment.estimated_delivery_time:
        order.estimated_delivery_time = assignment.estimated_delivery_time
    
    db.commit()
    db.refresh(order)
    
    # Notify delivery service
    try:
        async with httpx.AsyncClient() as client:
            await client.put(
                f"{delivery_service_url}/agents/{assignment.delivery_agent_id}/assign",
                json={"order_id": order_id}
            )
    except httpx.RequestError:
        pass
    
    return order

@router.post("/{order_id}/notify")
async def notify_new_order(order_id: int, db: Session = Depends(get_db)):
    """Endpoint for user service to notify about new orders"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Here you could add logic to notify restaurant (email, push notification, etc.)
    # For now, just return success
    return {"message": "Restaurant notified about new order", "order_id": order_id}

async def assign_delivery_agent(order_id: int, db: Session):
    """Auto-assign an available delivery agent to an order"""
    delivery_service_url = os.getenv("DELIVERY_SERVICE_URL", "http://localhost:8003")
    
    try:
        async with httpx.AsyncClient() as client:
            # Get available delivery agents
            agents_response = await client.get(
                f"{delivery_service_url}/agents/available"
            )
            if agents_response.status_code == 200:
                agents = agents_response.json()
                if agents:
                    # Assign the first available agent
                    agent = agents[0]
                    order = db.query(Order).filter(Order.id == order_id).first()
                    if order:
                        order.delivery_agent_id = agent["id"]
                        # Set estimated delivery time (30 minutes from now)
                        order.estimated_delivery_time = datetime.now() + timedelta(minutes=30)
                        db.commit()
                        
                        # Notify delivery service
                        await client.put(
                            f"{delivery_service_url}/agents/{agent['id']}/assign",
                            json={"order_id": order_id}
                        )
    
    except httpx.RequestError:
        # Log error but don't fail the status update
        pass

async def notify_status_change(order_id: int, status: str):
    """Notify other services about order status changes"""
    user_service_url = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
    delivery_service_url = os.getenv("DELIVERY_SERVICE_URL", "http://localhost:8003")
    
    try:
        async with httpx.AsyncClient() as client:
            # Notify user service (for user notifications)
            await client.post(
                f"{user_service_url}/orders/{order_id}/status-update",
                json={"status": status}
            )
            
            # Notify delivery service if order is ready for pickup
            if status == "ready":
                await client.post(
                    f"{delivery_service_url}/deliveries/{order_id}/ready",
                    json={"status": status}
                )
    
    except httpx.RequestError:
        # Log error but don't fail the main operation
        pass
