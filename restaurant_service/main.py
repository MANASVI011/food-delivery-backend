from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import httpx
import os
from dotenv import load_dotenv

from database import SessionLocal, engine
from models import Base
from routers import restaurants, menu_items, orders
from schemas import RestaurantResponse

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Restaurant Service",
    description="Food Delivery Restaurant Service API",
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
app.include_router(restaurants.router, prefix="/restaurants", tags=["restaurants"])
app.include_router(menu_items.router, prefix="/menu-items", tags=["menu-items"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])

@app.get("/")
async def root():
    return {"message": "Restaurant Service is running"}

@app.get("/restaurants/available", response_model=List[RestaurantResponse])
def get_available_restaurants(db: Session = Depends(get_db)):
    """Get all restaurants that are currently online"""
    from models import Restaurant
    restaurants = db.query(Restaurant).filter(Restaurant.is_online == True).all()
    return restaurants

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "restaurant_service"}
