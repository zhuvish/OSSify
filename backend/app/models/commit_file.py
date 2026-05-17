from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.postgres import Base

class CommitFile(Base):
    __tablename__ = "commit_files"

    id = Column(Integer, primary_key=True, index=True)
    commit_id = Column(Integer, ForeignKey("commits.id"), nullable=False)
    filename = Column(String, index=True)
    file_extension = Column(String, index=True)
    additions = Column(Integer)
    deletions = Column(Integer)
    changes = Column(Integer)
    status = Column(String)
    commit = relationship("Commit", back_populates="files")