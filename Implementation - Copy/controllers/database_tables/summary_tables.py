
import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum, ForeignKey, func, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, foreign, joinedload
from controllers.database import Base


# ---------------------------------------------------------------------
# management summary description
# ---------------------------------------------------------------------

class MSDescription(Base):
    __tablename__ = 'ms_description' 

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ms_id = Column(Integer, nullable=False, unique=True)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())

# ---------------------------------------------------------------------
# management summary -> high level risk
# ---------------------------------------------------------------------

class HighLevelRisk(Base):
    __tablename__ = 'high_level_risk'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    impact_category = Column(String, nullable=False)
    init_afr_value = Column(String, nullable=True)
    resid_afr_value = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())

# ---------------------------------------------------------------------
# management summary -> initial risk matrixs
# ---------------------------------------------------------------------

class InitialRiskMatriks(Base):
    __tablename__ = 'initialriskmatriks'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    risk = Column(String, nullable=True)
    negligible =Column(String, nullable=True)
    moderate =Column(String, nullable=True)
    major = Column(String, nullable=True)
    severe = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())

# ---------------------------------------------------------------------
# management summary -> residual risk matrixs
# ---------------------------------------------------------------------

class ResidRiskMatriks(Base):
    __tablename__ = 'residriskmatriks'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    risk = Column(String, nullable=True)
    negligible =Column(String, nullable=True)
    moderate =Column(String, nullable=True)
    major = Column(String, nullable=True)
    severe = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())  
