from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///sec_filings.db')

# Create database engine
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

# Create session factory
Session = sessionmaker(bind=engine)

def get_db():
    """Get database session"""
    db = Session()
    try:
        yield db
    finally:
        db.close()