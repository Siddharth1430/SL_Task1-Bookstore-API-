import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.models import Base  

# Load environment variables from .env
load_dotenv()

# Get the database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if DATABASE_URL is None
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in .env file!")

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create all tables in the database if they don’t exist 
Base.metadata.create_all(bind=engine)  

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
