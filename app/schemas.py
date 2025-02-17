from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: str
    published_year: Optional[int] = None
    isbn: str = Field(..., min_length=13, max_length=13, description="ISBN must be exactly 13 characters.")
    price: float

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    published_year: Optional[int] = None
    isbn: Optional[str] = Field(None, min_length=13, max_length=13, description="ISBN must be exactly 13 characters.")
    price: Optional[float] = None

class BookResponse(BookBase):
    id: uuid.UUID
    created_at: datetime  # Keep it as datetime but define json_encoders

    class Config:
        from_orm = True
        json_encoders = {datetime: lambda v: v.isoformat()}
