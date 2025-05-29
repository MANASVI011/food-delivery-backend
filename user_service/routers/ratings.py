from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Order, Rating
from schemas import RatingCreate, RatingResponse

router = APIRouter()

@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def create_rating(rating: RatingCreate, user_id: int, db: Session = Depends(get_db)):
    """Submit a rating for an order"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify order exists and belongs to user
    order = db.query(Order).filter(
        Order.id == rating.order_id,
        Order.user_id == user_id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or doesn't belong to user"
        )
    
    # Check if order is completed
    if order.status != "delivered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only rate completed orders"
        )
    
    # Check if rating already exists
    existing_rating = db.query(Rating).filter(
        Rating.order_id == rating.order_id,
        Rating.user_id == user_id
    ).first()
    
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating already exists for this order"
        )
    
    # Validate rating values
    if rating.restaurant_rating and (rating.restaurant_rating < 1 or rating.restaurant_rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant rating must be between 1 and 5"
        )
    
    if rating.delivery_rating and (rating.delivery_rating < 1 or rating.delivery_rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery rating must be between 1 and 5"
        )
    
    # Create rating
    db_rating = Rating(
        order_id=rating.order_id,
        user_id=user_id,
        restaurant_id=order.restaurant_id,
        delivery_agent_id=order.delivery_agent_id,
        restaurant_rating=rating.restaurant_rating,
        delivery_rating=rating.delivery_rating,
        restaurant_review=rating.restaurant_review,
        delivery_review=rating.delivery_review
    )
    
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    
    return db_rating

@router.get("/user/{user_id}", response_model=List[RatingResponse])
def get_user_ratings(user_id: int, db: Session = Depends(get_db)):
    """Get all ratings by a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
    return ratings

@router.get("/order/{order_id}", response_model=RatingResponse)
def get_order_rating(order_id: int, db: Session = Depends(get_db)):
    """Get rating for a specific order"""
    rating = db.query(Rating).filter(Rating.order_id == order_id).first()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found for this order"
        )
    return rating

@router.put("/{rating_id}", response_model=RatingResponse)
def update_rating(rating_id: int, rating_update: RatingCreate, user_id: int, db: Session = Depends(get_db)):
    """Update an existing rating"""
    rating = db.query(Rating).filter(
        Rating.id == rating_id,
        Rating.user_id == user_id
    ).first()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    # Validate rating values
    if rating_update.restaurant_rating and (rating_update.restaurant_rating < 1 or rating_update.restaurant_rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant rating must be between 1 and 5"
        )
    
    if rating_update.delivery_rating and (rating_update.delivery_rating < 1 or rating_update.delivery_rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery rating must be between 1 and 5"
        )
    
    # Update rating
    for field, value in rating_update.dict(exclude_unset=True).items():
        if field != "order_id":  # Don't allow changing order_id
            setattr(rating, field, value)
    
    db.commit()
    db.refresh(rating)
    
    return rating
