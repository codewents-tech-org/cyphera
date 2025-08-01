
import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum, ForeignKey, func, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, foreign, joinedload
from controllers.database import Base


# ---------------------------------------------------------------------
# risk assessment
# ---------------------------------------------------------------------

class RiskData(Base):
    __tablename__ = 'risk_data'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))   
    rd_id = Column(String, nullable=False)
    ds_id = Column(String, nullable=False)
    impact = Column(String, nullable=True)
    threat_id = Column(String, nullable=False)
    init_afr_level = Column(String, nullable=True)
    init_afr_value = Column(String, nullable=True)
    resid_afr_level = Column(String, nullable=True)
    resid_afr_value = Column(String, nullable=True)
    toe_configuration_id = Column(String, nullable=True)
    risk_treatment = Column(String, nullable=True)
    security_claims_id = Column(String, nullable=True)
    security_goal_id = Column(String, nullable=True)
    mitigated_by =  Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now()) 
