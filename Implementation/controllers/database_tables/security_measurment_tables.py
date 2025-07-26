
import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum, ForeignKey, func, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, foreign, joinedload
from controllers.database import Base


# ---------------------------------------------------------------------
# security claims
# ---------------------------------------------------------------------

class SecurityClaims(Base):
    __tablename__ = 'security_claims'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) 
    sc_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    assumption_id = Column(String, ForeignKey('assumptions.assumption_id'), nullable=True)
    responsible = Column(String, nullable=True)
    toe_configuration_id = Column(String, ForeignKey('toe_configuration.toe_configuration_id'), nullable=True)
    description = Column(String, nullable=True)
    comments = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now()) 
    vversion = Column(String, default='3')
    is_latest = Column(String, default='False')
    is_deleted = Column(String, default='False')

# ---------------------------------------------------------------------
# security goals
# ---------------------------------------------------------------------

class SecurityGoals(Base):
    __tablename__ = 'security_goals'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) 
    sg_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    responsible = Column(String, nullable=True)
    toe_configuration_id = Column(String, ForeignKey('toe_configuration.toe_configuration_id'), nullable=True)
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
# security controls
# ---------------------------------------------------------------------

class SecurityControls(Base):
    __tablename__ = 'security_controls'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))    
    scc_id = Column(String, nullable=False, unique=True)
    name =Column(String, nullable=False)
    security_goal_id = Column(String, ForeignKey('security_goals.sg_id'), nullable=True)
    description = Column(String, nullable=True)
    comments = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now()) 
    version = Column(String, default='3')
    is_latest = Column(String, default='False')
    is_deleted = Column(String, default='False')
