from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.exc import SQLAlchemyError  # Import SQLAlchemy exceptions
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///actions.db")

try:
    engine = create_engine(DATABASE_URL, echo=False)
    Base = declarative_base()

    class Action(Base):
        __tablename__ = 'actions'
        action_id = Column(Integer, primary_key=True)
        description = Column(String)
        execute_at = Column(DateTime)
        status = Column(String)
        user_id = Column(Integer, ForeignKey('users.user_id'))

    Base.metadata.create_all(engine)

    Session_factory = sessionmaker(bind=engine)
    Session = scoped_session(Session_factory)

except SQLAlchemyError as e:
    print(f"Error initializing database: {e}")
    # Depending on requirements, here you might raise an error or exit

def main():
    session = Session()
    try:
        # Here you would include database operations
        # Example: 
        # new_action = Action(description='Test', execute_at=datetime.now(), status='pending', user_id=1)
        # session.add(new_action)
        # session.commit()
        print("Main function placeholder")
    except SQLAlchemyError as e:
        print(f"Database operation failed: {e}")
        session.rollback()  # Roll back the changes if any error occurs
    finally:
        session.close()

if __name__ == "__main__":
    main()