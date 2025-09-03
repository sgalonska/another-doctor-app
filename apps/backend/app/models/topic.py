import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, ARRAY, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Topic(Base):
    __tablename__ = "topic"

    topic_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    synonyms = Column(ARRAY(String), nullable=True)
    
    # Relationships
    doctor_scores = relationship("DoctorTopicScore", back_populates="topic")

class DoctorTopicScore(Base):
    __tablename__ = "doctor_topic_score"

    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctor.doctor_id"), primary_key=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topic.topic_id"), primary_key=True)
    components = Column(JSONB, nullable=True)  # {pubs_5y:3, trials_pi:1, grants:2, inst_pubs:25,...}
    score = Column(Numeric, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    doctor = relationship("Doctor", back_populates="topic_scores")
    topic = relationship("Topic", back_populates="doctor_scores")