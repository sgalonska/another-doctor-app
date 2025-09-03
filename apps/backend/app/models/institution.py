import uuid
from sqlalchemy import Column, String, Text, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base

class Institution(Base):
    __tablename__ = "institution"

    institution_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(ARRAY(Text), nullable=False)
    name = Column(String, nullable=False)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())