from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///actions.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Base class for our classes definitions
Base = declarative_base()

# Define Action model
class Action(Base):
    __tablename__ = 'actions'

    # Define columns
    action_id = Column(Integer, primary_key=True)
    description = Column(String)
    execute_at = Column(DateTime)
    status = Column(String)
    user_id = Column(Integer, ForeignKey('users.user_id'))

# Create tables
Base.metadata.create_all(engine)

# Create a sessionmaker
Session = sessionmaker(bind=engine)