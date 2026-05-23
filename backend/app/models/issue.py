from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.app.db.postgres import Base

class Issue(Base):
    __tablename__ = "issues"

    __table_args__ = (
        UniqueConstraint("repo_id", "issue_number", name="uq_repo_issue"),
    )

    id = Column(Integer, primary_key=True, index=True)
    issue_number = Column(Integer, nullable=False, index=True)
    title = Column(String)
    body = Column(String)
    state = Column(String)
    created_at = Column(DateTime)
    closed_at = Column(DateTime)
    labels = Column(String)
    comments_count = Column(Integer)
    author_login = Column(String, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("contributors.id"))
    contributor = relationship("Contributor", back_populates="issues")
    repository = relationship("Repository", back_populates="issues")