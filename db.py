from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError  # Import SQLAlchemy exceptions
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

Session = sessionmaker(bind=engine)

def get_db_connection():
    db_session = Session()
    try:
        yield db_session
    except SQLAlchemyError as e:
        print(f"An error occurred while handling the database operation: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        db_session.close()