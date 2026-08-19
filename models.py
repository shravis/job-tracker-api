from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    Index,
    DateTime,
    func
)
from sqlalchemy.orm import declarative_base, relationship
from database import engine

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)

    jobs = relationship(
        "Job",
        back_populates="owner",
        cascade="all, delete"
    )


class Job(Base):
    __tablename__ = "jobs"

    __table_args__ = (
        Index("idx_jobs_company", "company"),
        Index("idx_jobs_status", "status"),
    )

    id = Column(Integer, primary_key=True)
    company = Column(Text, nullable=False)
    position = Column(Text, nullable=False)
    status = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    owner = relationship(
        "User",
        back_populates="jobs"
    )


Base.metadata.create_all(bind=engine)