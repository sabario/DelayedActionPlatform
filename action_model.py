from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///actions.db")

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

def main():
    session = Session()
    try:
        pass
    finally:
        session.close()

if __name__ == "__main__":
    main()