from typing import Optional
from pydantic import BaseModel, Field, constr
from sqlalchemy import Column, Integer, String, Float
from database import Base

# SQLAlchemy Models
class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String)
    amount = Column(Integer)
    price = Column(Float)
    description = Column(String, nullable=True)

# Pydantic Models
class ItemBase(BaseModel):
    sku: constr(min_length=1) = Field(..., description="Stock Keeping Unit - must be unique")
    name: str = Field(..., min_length=1, description="Name of the item")
    amount: int = Field(..., ge=0, description="Quantity in stock")
    price: float = Field(..., ge=0, description="Price of the item")
    description: Optional[str] = Field(None, description="Item description")

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
