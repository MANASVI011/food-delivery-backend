from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# User schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Order Item schemas
class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int
    price: Decimal
    special_requests: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    
    class Config:
        from_attributes = True

# Order schemas
class OrderBase(BaseModel):
    restaurant_id: int
    delivery_address: str
    special_instructions: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderResponse(OrderBase):
    id: int
    user_id: int
    delivery_agent_id: Optional[int] = None
    status: str
    total_amount: Decimal
    order_time: datetime
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True

# Rating schemas
class RatingBase(BaseModel):
    restaurant_rating: Optional[int] = None
    delivery_rating: Optional[int] = None
    restaurant_review: Optional[str] = None
    delivery_review: Optional[str] = None

class RatingCreate(RatingBase):
    order_id: int

class RatingResponse(RatingBase):
    id: int
    order_id: int
    user_id: int
    restaurant_id: int
    delivery_agent_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Restaurant schemas (for external service responses)
class RestaurantResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    address: str
    phone: str
    email: Optional[str] = None
    cuisine_type: Optional[str] = None
    is_online: bool
    rating: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Menu Item schemas (for external service responses)
class MenuItemResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    category: Optional[str] = None
    is_available: bool
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
