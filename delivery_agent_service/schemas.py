from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# Delivery Agent schemas
class DeliveryAgentBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    vehicle_type: Optional[str] = None
    current_location: Optional[str] = None

class DeliveryAgentCreate(DeliveryAgentBase):
    pass

class DeliveryAgentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    vehicle_type: Optional[str] = None
    is_available: Optional[bool] = None
    current_location: Optional[str] = None

class DeliveryAgentResponse(DeliveryAgentBase):
    id: int
    is_available: bool
    rating: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Delivery schemas
class DeliveryBase(BaseModel):
    pickup_address: str
    delivery_address: str
    notes: Optional[str] = None

class DeliveryCreate(DeliveryBase):
    order_id: int
    delivery_agent_id: int

class DeliveryStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class DeliveryResponse(DeliveryBase):
    id: int
    order_id: int
    delivery_agent_id: int
    status: str
    pickup_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    agent: Optional[DeliveryAgentResponse] = None
    
    class Config:
        from_attributes = True

# Agent Assignment
class AgentAssignment(BaseModel):
    order_id: int

# Agent Status Update
class AgentStatusUpdate(BaseModel):
    is_available: bool
    current_location: Optional[str] = None
