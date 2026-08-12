from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import declarative_base
from database import engine

Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    company = Column(Text, nullable=False)
    position = Column(Text, nullable=False)
    status = Column(Text, nullable=False)


Base.metadata.create_all(bind=engine)