from fastapi import FastAPI
from app.api import books
from app.connection import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the book routes
app.include_router(books.router)
