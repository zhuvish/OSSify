from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.app.db.postgres import Base

class PullRequest(Base):
    __tablename__ = "pull_requests"
    __table_args__ = (
        UniqueConstraint("repo_id", "pr_number", name="uq_repo_pr"),
    )

    id = Column(Integer, primary_key=True, index=True)
    pr_number = Column(Integer, nullable=False, index=True)
    title = Column(String)
    body = Column(String)
    state = Column(String)
    created_at = Column(DateTime)
    closed_at = Column(DateTime)
    merged = Column(Boolean)
    merged_at = Column(DateTime)
    comments_count = Column(Integer)
    review_comments_count = Column(Integer)
    author_login = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("contributors.id"))
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    repository = relationship("Repository", back_populates="pull_requests")
    contributor = relationship("Contributor", back_populates="pull_requests")