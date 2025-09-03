import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Doctor(Base):
    __tablename__ = "doctor"

    doctor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    orcid = Column(String, nullable=True)
    npi = Column(String, nullable=True)
    primary_specialty = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    affiliations = relationship("DoctorAffiliation", back_populates="doctor")
    works = relationship("DoctorWork", back_populates="doctor")
    topic_scores = relationship("DoctorTopicScore", back_populates="doctor")

class DoctorAffiliation(Base):
    __tablename__ = "doctor_affiliation"

    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctor.doctor_id"), primary_key=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institution.institution_id"), primary_key=True)
    role = Column(String, primary_key=True)
    start_year = Column(Integer, primary_key=True)
    end_year = Column(Integer, nullable=True)
    
    # Relationships
    doctor = relationship("Doctor", back_populates="affiliations")
    institution = relationship("Institution")