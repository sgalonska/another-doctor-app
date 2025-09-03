import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Work(Base):
    __tablename__ = "work"

    work_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String, nullable=False)  # 'pubmed'|'openalex'|'crossref'|'ctgov'|'nih_reporter'|'euctr'
    source_key = Column(String, nullable=False)  # PMID | DOI | OpenAlex ID | NCT ID | ProjectNum
    title = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    doi = Column(String, nullable=True)
    mesh_terms = Column(ARRAY(Text), nullable=True)
    url = Column(String, nullable=True)
    raw = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    authors = relationship("DoctorWork", back_populates="work")

class DoctorWork(Base):
    __tablename__ = "doctor_work"

    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctor.doctor_id"), primary_key=True)
    work_id = Column(UUID(as_uuid=True), ForeignKey("work.work_id"), primary_key=True)
    author_position = Column(Integer, nullable=True)
    is_pi = Column(Boolean, nullable=True)
    
    # Relationships
    doctor = relationship("Doctor", back_populates="works")
    work = relationship("Work", back_populates="authors")