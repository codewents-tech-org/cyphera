
import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum, ForeignKey, func, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, foreign, joinedload
from controllers.database import Base


# ---------------------------------------------------------------------
# threat catalog
# ---------------------------------------------------------------------

class ThreatCatalog(Base):
    __tablename__ = 'threat_catalog'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) 
    security_controls = Column(String, nullable=True)
    mitigation_checkbox = Column(String, nullable=True)
    attack_or_vulnerability_checkbox = Column(String, nullable=True)
    threat_id = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now()) 
