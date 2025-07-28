
import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum, ForeignKey, func, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, foreign, joinedload
from controllers.database import Base


class MindmapNodeType(enum.Enum):
    HEAD = "HEAD"
    INTERMEDIATE = "INTERMEDIATE"
    LEAF = "LEAF"

# ---------------------------------------------------------------------
# system description
# ---------------------------------------------------------------------

class SystemDescription(Base):
    __tablename__ = 'system_description' 

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    toe_id = Column(Integer, nullable=False, unique=True)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())

# ---------------------------------------------------------------------
# scope description
# ---------------------------------------------------------------------

class ScopeDescription(Base):
    __tablename__ = 'scope_description'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scope_id = Column(Integer, nullable=False, unique=True)
    scope_content = Column(String, nullable=False)
    scope_timestamp = Column(DateTime, default=func.now())
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())

# ---------------------------------------------------------------------
# Scopes - All scopes
# ---------------------------------------------------------------------

class ScopeHomeMindmap(Base):
    __tablename__ = 'scope_home_mindmap'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scope_id = Column(String, nullable=False, unique=True)
    scope_name = Column(String, nullable=False)
    comments = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())
    version = Column(String, default='3')
    is_latest = Column(String, default='False')
    is_deleted = Column(String, default='False')

# ---------------------------------------------------------------------
# Mindmap - All scopes mindmap
# ---------------------------------------------------------------------

class ScopeMindmaps(Base):
    __tablename__ = 'scope_mindmaps'

    uuid: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("scope_mindmaps.uuid", ondelete="SET NULL"))
    scope_id: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[Optional[str]] = mapped_column(String, nullable=False)
    node_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    node_desc: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    node_type: Mapped[MindmapNodeType] = mapped_column(Enum(MindmapNodeType), nullable=False)
    pos_x: Mapped[str] = mapped_column(String, nullable=False)
    pos_y: Mapped[str] = mapped_column(String, nullable=False)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_by: Mapped[Optional[str]] = mapped_column(String)
    updated_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[str] = mapped_column(String, default="3")

# ---------------------------------------------------------------------
# Mindmap - mindmap to attack tree generation table
# ---------------------------------------------------------------------

class ScopesReference(Base):
    __tablename__ = 'scopes_references'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) 
    scope_id = Column(String, nullable=False)
    scope_name = Column(String, nullable=False)
    asset_id = Column(String, ForeignKey('assets.asset_id'), nullable=True)
    threat_id = Column(String, ForeignKey('threat.threat_id'), nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now()) 
    version: Mapped[str] = mapped_column(String, default="3")

# ---------------------------------------------------------------------
# assumptions
# ---------------------------------------------------------------------

class Assumptions(Base):
    __tablename__ = 'assumptions'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) 
    assumption_id = Column(String, nullable=False, unique=True)
    assumptions = Column(String, nullable=False)
    comments = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())  
    version = Column(String, default='3')
    is_latest = Column(String, default='False')
    is_deleted = Column(String, default='False')

# ---------------------------------------------------------------------
# misuse cases
# ---------------------------------------------------------------------

class Misusecases(Base):
    __tablename__ = 'misuse_cases'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) 
    misuse_cases_id = Column(String, nullable=False, unique=True)
    misuse_cases_name = Column(String, nullable=False)
    misuse_cases_comments = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())  
    version = Column(String, default='3')
    is_latest = Column(String, default='False')
    is_deleted = Column(String, default='False')

# ---------------------------------------------------------------------
# toe configurations
# ---------------------------------------------------------------------

class TOEConfiguration(Base):
    __tablename__ = 'toe_configuration'

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))    
    toe_configuration_id = Column(String, nullable=False, unique=True)
    toe_configuration_name = Column(String, nullable=False)
    toe_configuration_description = Column(String, nullable=True)
    toe_configuration_comments = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())  
    vversion = Column(String, default='3')
    is_latest = Column(String, default='False')
    is_deleted = Column(String, default='False')
