import uuid
from sqlalchemy import Column, String, DateTime, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.db.base import Base

class CaseSpec(Base):
    __tablename__ = "case_spec"

    case_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    casejson = Column(JSONB, nullable=False)  # de-identified machine-readable case
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(String, default="v1")

class TermCache(Base):
    __tablename__ = "term_cache"

    lemma = Column(String, primary_key=True)
    mesh = Column(ARRAY(Text), nullable=True)
    snomed = Column(ARRAY(Text), nullable=True)
    icd10 = Column(ARRAY(Text), nullable=True)
    canonical_label = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())