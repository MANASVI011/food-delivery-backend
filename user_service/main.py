from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import httpx
import os
from dotenv import load_dotenv

from database import SessionLocal, engine
from models import Base
from routers import users, orders, ratings
from schemas import RestaurantResponse

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    description="Food Delivery User Service API",
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
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(ratings.router, prefix="/ratings", tags=["ratings"])

@app.get("/")
async def root():
    return {"message": "User Service is running"}

@app.get("/restaurants/available", response_model=List[RestaurantResponse])
async def get_available_restaurants():
    """Get all restaurants that are currently online"""
    restaurant_service_url = os.getenv("RESTAURANT_SERVICE_URL", "http://localhost:8002")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{restaurant_service_url}/restaurants/available")
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Restaurant service unavailable"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to restaurant service"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user_service"}
