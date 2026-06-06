from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from backend.app.db.postgres import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    full_name = Column(String, unique=True, nullable=False, index=True)
    url = Column(String, nullable=False)
    description = Column(String)
    primary_language = Column(String)
    stars = Column(Integer)
    forks = Column(Integer)
    open_issues_count = Column(Integer)
    default_branch = Column(String)
    github_created_at = Column(DateTime)
    github_updated_at = Column(DateTime)
    # processing status: 'processing' | 'ready' | 'failed'
    status = Column(String, nullable=True)
    processing_stage = Column(String, nullable=True)
    commits = relationship("Commit", back_populates="repository", cascade="all, delete-orphan")
    pull_requests = relationship("PullRequest", back_populates="repository", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="repository", cascade="all, delete-orphan")