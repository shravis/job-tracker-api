from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    Text,
    ForeignKey,
    Index,
    DateTime,
    func
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Keep in sync with VALID_STATUSES in
# alembic/versions/f9a0b1c2d3e4_jobs_status_check.py and
# schemas.JobStatus. This is what the test suite's create_all()
# schema enforces, mirroring the ck_jobs_status constraint that the
# migration adds in real environments.
VALID_JOB_STATUSES = (
    "Applied",
    "Interview",
    "Offer",
    "Accepted",
    "Rejected",
    "Withdrawn",
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    token_version = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

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
        Index("idx_jobs_user_id", "user_id"),
        CheckConstraint(
            "status IN ({})".format(
                ", ".join(f"'{s}'" for s in VALID_JOB_STATUSES)
            ),
            name="ck_jobs_status",
        ),
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