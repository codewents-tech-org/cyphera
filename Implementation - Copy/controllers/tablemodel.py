"""
📦 Module        : tablemodel.py
🧱 Layer         : Data Layer
🔖 Module ID     : None
📋 Requirement ID(s): None
🧑‍💻 Developed By : ES101 Vishnu Viswanath
🕒 Created On    : 2025-05-02
🧾 File Version  : v1.0.0
🧾 Updated by: ES101 Vishnu Viswanath
🧾 Updated on: 2025-05-14
 
🧠 Description:
This module defines the ORM (Object Relational Mapping) models for the application,
representing all core business entities used in database interactions. It uses SQLAlchemy
as the ORM layer and includes table structures, default values, and relationships between
entities.

🎯 Responsibilities:
- Define SQLAlchemy ORM table classes for all modules (scope, assets, threats, etc.)
- Provide field metadata such as type, nullability, default values, and foreign key links
- Establish a central schema for consistent database interaction across the application
- Ensure UUID-based primary keys and automatic timestamps for auditing
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from controllers.database import Base
import uuid
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from controllers.database_tables.target_of_evaluation_tables import (
                                                                        MindmapNodeType,
                                                                        SystemDescription,
                                                                        ScopeDescription,
                                                                        ScopeHomeMindmap,
                                                                        ScopeMindmaps,
                                                                        ScopesReference,
                                                                        Assumptions,
                                                                        Misusecases,
                                                                        TOEConfiguration
                                                                    )
from controllers.database_tables.analysis_tables import (
                                                            Assets,
                                                            DamageScenarios,
                                                            Threats,
                                                            ThreatScenarios
                                                        )
from controllers.database_tables.security_measurment_tables import (
                                                                        SecurityClaims,
                                                                        SecurityGoals,
                                                                        SecurityControls
                                                                    )
from controllers.database_tables.catalog_tables import ThreatCatalog
from controllers.database_tables.attack_paths_tables import (
                                                                NodeType,
                                                                AttackLeafNodes,
                                                                AttackIntermediateNodes,
                                                                TechnicalTreeHome,
                                                                TechnicalAttackTree,
                                                                RiskControlTreeHome,
                                                                RiskControlTree,
                                                                AttackTreeHome,
                                                                AttackTree,
                                                                ReferenceTrees
                                                            )
from controllers.database_tables.risk_assessment_tables import RiskData
from controllers.database_tables.summary_tables import (
                                                            MSDescription,
                                                            HighLevelRisk,
                                                            InitialRiskMatriks,
                                                            ResidRiskMatriks
                                                        )


# ---------------------------------------------------------------------
# database activity log
# ---------------------------------------------------------------------

class ActivityLog(Base):
    __tablename__ = 'activity_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_type = Column(String(20))     # CREATE / READ / UPDATE / DELETE
    module = Column(String(50))          # e.g., 'job', 'login'
    entity_id = Column(String(100))      # Record or item affected
    performed_by = Column(String(50))    # User ID or 'system'
    description = Column(String(255))    # Human-readable description
    timestamp = Column(DateTime, default=datetime.utcnow)
     
    
    






 















        

