from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from backend.app.db.postgres import Base

class Contributor(Base):
    __tablename__ = "contributors"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=False, index=True)
    profile_url = Column(String)
    avatar_url = Column(String)
    contributions_count = Column(Integer)
    display_name = Column(String)
    bio = Column(String)
    company = Column(String)
    location = Column(String)
    followers = Column(Integer)
    public_repos = Column(Integer)
    github_created_at = Column(DateTime)
    commits = relationship("Commit", back_populates="contributor")
    issues = relationship("Issue", back_populates="contributor")
    pull_requests = relationship("PullRequest", back_populates="contributor")
