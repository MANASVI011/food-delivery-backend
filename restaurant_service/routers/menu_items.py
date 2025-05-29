from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Restaurant, MenuItem
from schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse

router = APIRouter()

@router.post("/restaurant/{restaurant_id}", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(restaurant_id: int, menu_item: MenuItemCreate, db: Session = Depends(get_db)):
    """Add a new menu item to a restaurant"""
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    db_menu_item = MenuItem(restaurant_id=restaurant_id, **menu_item.dict())
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

@router.get("/{menu_item_id}", response_model=MenuItemResponse)
def get_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    """Get menu item by ID"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    return menu_item

@router.get("/restaurant/{restaurant_id}", response_model=List[MenuItemResponse])
def get_restaurant_menu(restaurant_id: int, available_only: bool = False, db: Session = Depends(get_db)):
    """Get all menu items for a restaurant"""
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    query = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id)
    
    if available_only:
        query = query.filter(MenuItem.is_available == True)
    
    menu_items = query.all()
    return menu_items

@router.put("/{menu_item_id}", response_model=MenuItemResponse)
def update_menu_item(menu_item_id: int, menu_item_update: MenuItemUpdate, db: Session = Depends(get_db)):
    """Update menu item information"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    for field, value in menu_item_update.dict(exclude_unset=True).items():
        setattr(menu_item, field, value)
    
    db.commit()
    db.refresh(menu_item)
    return menu_item

@router.put("/{menu_item_id}/availability", response_model=MenuItemResponse)
def update_menu_item_availability(menu_item_id: int, is_available: bool, db: Session = Depends(get_db)):
    """Update menu item availability"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    menu_item.is_available = is_available
    db.commit()
    db.refresh(menu_item)
    return menu_item

@router.delete("/{menu_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    """Delete a menu item"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    db.delete(menu_item)
    db.commit()
    return None
