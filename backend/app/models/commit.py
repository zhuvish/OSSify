from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.db.postgres import Base

class Commit(Base):
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)
    sha = Column(String, unique=True, nullable=False, index=True)
    message = Column(String)
    author_name = Column(String)
    author_email = Column(String)
    date = Column(DateTime)
    additions = Column(Integer)
    deletions = Column(Integer)
    total_changes = Column(Integer)
    commit_url = Column(String)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    contributor_id = Column(Integer, ForeignKey("contributors.id"), nullable=True)
    repository = relationship("Repository", back_populates="commits")
    contributor = relationship("Contributor", back_populates="commits")
    files = relationship("CommitFile", back_populates="commit", cascade="all, delete-orphan")