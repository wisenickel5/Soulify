# Initialize the Soulify DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(engine)
