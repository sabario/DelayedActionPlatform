from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError  # Import SQLAlchemy exceptions
from dotenv import load_dotenv
import os
import logging  # Import logging library

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

Session = sessionmaker(bind=engine)

def get_db_connection():
    db_session = Session()
    try:
        logger.info("Database connection established")
        yield db_session
    except SQLAlchemyError as e:
        logger.error(f"An error occurred while handling the database operation: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        db_session.close()
        logger.info("Database connection closed")

def log_database_operation(func):
    """
    A decorator to log the database operation.
    """
    def wrapper(*args, **kwargs):
        logger.info(f"Operation '{func.__name__}' started")
        result = func(*args, **kwargs)
        logger.info(f"Operation '{func.__name__}' finished")
        return result
    return wrapper

# Example usage of the new functionality
@log_database_operation
def example_database_operation():
    # This function should include the actual database operation you intend to perform.
    # For this example, it simply logs that the operation would occur here.
    logger.info("Performing a sample database operation...")

# Remember to call your example function to see it in action
if __name__ == "__main__":
    with get_db_connection() as connection:
        example_database_operation()