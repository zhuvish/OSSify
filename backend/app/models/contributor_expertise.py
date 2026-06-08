from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.db.postgres import Base

class ContributorExpertise(Base):
    __tablename__ = "contributor_expertise"

    id = Column(Integer, primary_key=True, index=True)
    contributor_id = Column(Integer, ForeignKey("contributors.id"), nullable=False)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    domain = Column(String, nullable=False, index=True)
    score = Column(Float, default=0.0)
    evidence_count = Column(Integer, default=0)
    source = Column(String, nullable=False)
    confidence = Column(Float, default=0.5)
    contributor = relationship("Contributor")