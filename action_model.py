from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.exc import SQLAlchemyError  # Import SQLAlchemy exceptions
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
import os
from datetime import datetime
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
    # Depending on requirements, you might raise an error or exit


def add_action(session, description, execute_at, status, user_id):
    """
    Adds a new action into the database.

    Args:
        session: Database session.
        description (str): Description of the action.
        execute_at (DateTime): The time at which the action should be executed.
        status (str): Status of the action.
        user_id (int): ID of the user associated with the action.
    """
    try:
        new_action = Action(description=description, execute_at=execute_at, status=status, user_id=user_id)
        session.add(new_action)
        session.commit()
        print("Action added successfully.")
    except SQLAlchemyError as e:
        print(f"Error adding action: {e}")
        session.rollback()


def main():
    session = Session()
    try:
        # Demonstration of adding an action
        add_action(session, 'Test Action', datetime.now(), 'pending', 1)
    except SQLAlchemyError as e:
        print(f"Database operation failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()