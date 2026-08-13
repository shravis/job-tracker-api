from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import declarative_base
from database import engine

Base = declarative_base()

# Job table
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    company = Column(Text, nullable=False)
    position = Column(Text, nullable=False)
    status = Column(Text, nullable=False)


# User table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)


# Create tables in the database
Base.metadata.create_all(bind=engine)