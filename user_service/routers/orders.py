from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import httpx
import os
from decimal import Decimal

from database import get_db
from models import User, Order, OrderItem
from schemas import OrderCreate, OrderResponse

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(order: OrderCreate, user_id: int, db: Session = Depends(get_db)):
    """Place a new order"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify restaurant is available and get menu items
    restaurant_service_url = os.getenv("RESTAURANT_SERVICE_URL", "http://localhost:8002")
    
    try:
        async with httpx.AsyncClient() as client:
            # Check restaurant availability
            restaurant_response = await client.get(
                f"{restaurant_service_url}/restaurants/{order.restaurant_id}"
            )
            if restaurant_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurant not found"
                )
            
            restaurant_data = restaurant_response.json()
            if not restaurant_data.get("is_online"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Restaurant is currently offline"
                )
            
            # Verify menu items and calculate total
            total_amount = Decimal('0.00')
            for item in order.items:
                menu_response = await client.get(
                    f"{restaurant_service_url}/menu-items/{item.menu_item_id}"
                )
                if menu_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Menu item {item.menu_item_id} not found"
                    )
                
                menu_item = menu_response.json()
                if not menu_item.get("is_available"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Menu item {menu_item['name']} is not available"
                    )
                
                # Verify price matches
                if abs(float(item.price) - float(menu_item["price"])) > 0.01:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Price mismatch for item {menu_item['name']}"
                    )
                
                total_amount += item.price * item.quantity
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to restaurant service"
        )
    
    # Create order
    db_order = Order(
        user_id=user_id,
        restaurant_id=order.restaurant_id,
        total_amount=total_amount,
        delivery_address=order.delivery_address,
        special_instructions=order.special_instructions,
        status="pending"
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items
    for item in order.items:
        db_order_item = OrderItem(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price=item.price,
            special_requests=item.special_requests
        )
        db.add(db_order_item)
    
    db.commit()
    
    # Notify restaurant service about new order
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{restaurant_service_url}/orders/{db_order.id}/notify",
                json={"order_id": db_order.id, "status": "pending"}
            )
    except httpx.RequestError:
        # Log error but don't fail the order creation
        pass
    
    # Refresh to get order items
    db.refresh(db_order)
    return db_order

@router.get("/user/{user_id}", response_model=List[OrderResponse])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    """Get all orders for a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    orders = db.query(Order).filter(Order.user_id == user_id).all()
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

@router.put("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: int, user_id: int, db: Session = Depends(get_db)):
    """Cancel an order (only if status is pending)"""
    order = db.query(Order).filter(
        Order.id == order_id, 
        Order.user_id == user_id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only cancel pending orders"
        )
    
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    
    # Notify restaurant service
    restaurant_service_url = os.getenv("RESTAURANT_SERVICE_URL", "http://localhost:8002")
    try:
        async with httpx.AsyncClient() as client:
            await client.put(
                f"{restaurant_service_url}/orders/{order_id}/status",
                json={"status": "cancelled"}
            )
    except httpx.RequestError:
        pass
    
    return order
