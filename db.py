from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

Session = scoped_session(sessionmaker(bind=engine))

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
    def wrapper(*args, **kwargs):
        logger.info(f"Operation '{func.__name__}' started")
        result = func(*args, **kwargs)
        logger.info(f"Operation '{func.__name__}' finished")
        return result
    return wrapper

@log_database_operation
def example_bulk_insert_operation(session, data):
    try:
        logger.info("Performing a bulk insert...")
    except Exception as e:
        logger.error(f"An error occurred during bulk insert operation: {e}")

def batch_process(func, data, batch_size=100):
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        func(batch)

if __name__ == "__main__":
    data = [...]  
    with get_db_connection() as connection:
        example_bulk_insert_operation(connection, data)