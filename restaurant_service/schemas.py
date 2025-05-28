from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# Restaurant schemas
class RestaurantBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    phone: str
    email: Optional[EmailStr] = None
    cuisine_type: Optional[str] = None

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    cuisine_type: Optional[str] = None
    is_online: Optional[bool] = None

class RestaurantResponse(RestaurantBase):
    id: int
    is_online: bool
    rating: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Menu Item schemas
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category: Optional[str] = None
    image_url: Optional[str] = None

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = None

class MenuItemResponse(MenuItemBase):
    id: int
    restaurant_id: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Order schemas
class OrderStatusUpdate(BaseModel):
    status: str

class OrderResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    delivery_agent_id: Optional[int] = None
    status: str
    total_amount: Decimal
    delivery_address: str
    special_instructions: Optional[str] = None
    order_time: datetime
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Delivery Agent Assignment
class DeliveryAgentAssignment(BaseModel):
    delivery_agent_id: int
    estimated_delivery_time: Optional[datetime] = None
