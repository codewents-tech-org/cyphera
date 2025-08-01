
import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum, ForeignKey, func, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, foreign, joinedload
from controllers.database import Base


# ---------------------------------------------------------------------
# assets
# ---------------------------------------------------------------------

class Assets(Base):
    __tablename__ = 'assets'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))   
    asset_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    security_properties =  Column(String, nullable=True)
    description = Column(String, nullable=True)
    comments =  Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())  
    version = Column(String, default='3')
    is_latest = Column(String, default='False')
    is_deleted = Column(String, default='False')

# ---------------------------------------------------------------------
# damage scenarios
# ---------------------------------------------------------------------

class DamageScenarios(Base):
    __tablename__ = 'damage_scenarios'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) 
    ds_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    impact = Column(String, nullable=True)
    impact_category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    comments = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())  
    version = Column(String, default='3')
    is_latest = Column(String, default='False')
    is_deleted = Column(String, default='False')

# ---------------------------------------------------------------------
# threats
# ---------------------------------------------------------------------

class Threats(Base):
    __tablename__ = 'threat'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) 
    threat_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    ds_id = Column(String, nullable=True)
    toe_configuration_id = Column(String, nullable=True)
    misuse_cases_id = Column(String, nullable=True)
    initia_afr = Column(String, nullable=True)
    resid_afr = Column(String, nullable=True)
    asset_id = Column(String, nullable=False)
    security_properties = Column(String, nullable=True)
    reasoning = Column(String, nullable=True)
    comments = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now()) 
    version = Column(String, default='3')
    is_latest = Column(String, default='False')
    is_deleted = Column(String, default='False')

# ---------------------------------------------------------------------
# threat scenarios
# ---------------------------------------------------------------------

class ThreatScenarios(Base):
    __tablename__ = 'threat_scenarios'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))   
    ts_id = Column(String, nullable=False, unique=True)
    threat_id = Column(String, nullable=False)
    ds_id = Column(String, nullable=False)
    toe_configuration_id = Column(String, nullable=True)
    reasoning = Column(String, nullable=True)
    comments = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now()) 
    version = Column(String, default='3')
    is_latest = Column(String, default='False')
    is_deleted = Column(String, default='False')
