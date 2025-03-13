from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from models import Item, ItemCreate, ItemDB
from database import get_db, engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React's default dev server port
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello"}

@app.get("/about")
def about() -> dict[str, str]:
    return {"message": "This is the about page."}

# Item CRUD Operations
@app.post("/items", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(get_db)) -> Item:
    try:
        db_item = ItemDB(
            sku=item.sku,
            name=item.name,
            amount=item.amount,
            price=item.price,
            description=item.description
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="SKU already exists")

@app.get("/items", response_model=List[Item])
def list_items(db: Session = Depends(get_db)) -> List[Item]:
    return db.query(ItemDB).all()

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int, db: Session = Depends(get_db)) -> Item:
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)) -> Item:
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    try:
        # Update item attributes
        for key, value in item.dict().items():
            setattr(db_item, key, value)
        
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="SKU already exists")

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}