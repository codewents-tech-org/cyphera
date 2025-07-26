
import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum, ForeignKey, func, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, foreign, joinedload
from controllers.database import Base
from controllers.schema_manager import get_first_instance, get_instances


class NodeType(enum.Enum):
    HEAD = "head"
    INTERMEDIATE = "intermediate"
    LEAF = "leaf"
    TAT_HEAD = "technical head"
    RCT_HEAD = "control head"
    RCT_TAT_HEAD = "technical head"

# ---------------------------------------------------------------------
# Leaf Nodes - All Attack Paths leaf nodes (attack leaves)
# ---------------------------------------------------------------------

class AttackLeafNodes(Base):
    """Leaf node details."""
    __tablename__ = "attack_leaf_nodes"

    uuid: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    time: Mapped[Optional[str]] = mapped_column(String)
    expertise: Mapped[Optional[str]] = mapped_column(String)
    knowledge: Mapped[Optional[str]] = mapped_column(String)
    access: Mapped[Optional[str]] = mapped_column(String)
    equipment: Mapped[Optional[str]] = mapped_column(String)
    afr_level: Mapped[Optional[str]] = mapped_column(String)
    reasoning: Mapped[Optional[str]] = mapped_column(String)
    comments: Mapped[Optional[str]] = mapped_column(String)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_by: Mapped[Optional[str]] = mapped_column(String)
    updated_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[str] = mapped_column(String, default="3")
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    technical_nodes = relationship(
        "TechnicalAttackTree",
        primaryjoin="AttackLeafNodes.uuid == foreign(TechnicalAttackTree.node_uuid)",
        viewonly=True
    )

    riskcontrol_nodes = relationship(
        "RiskControlTree",
        primaryjoin="AttackLeafNodes.uuid == foreign(RiskControlTree.node_uuid)",
        viewonly=True
    )

    attack_tree_nodes = relationship(
        "AttackTree",
        primaryjoin="AttackLeafNodes.uuid == foreign(AttackTree.node_uuid)",
        viewonly=True
    )

# ---------------------------------------------------------------------
# Intermediate Nodes - All Attack Paths intermediate nodes
# ---------------------------------------------------------------------

class AttackIntermediateNodes(Base):
    """Intermediate node details."""
    __tablename__ = "attack_intermediate_nodes"

    uuid: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_by: Mapped[Optional[str]] = mapped_column(String)
    updated_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[str] = mapped_column(String, default="3")
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    technical_nodes = relationship(
        "TechnicalAttackTree",
        primaryjoin="AttackIntermediateNodes.uuid == foreign(TechnicalAttackTree.node_uuid)",
        viewonly=True
    )

    riskcontrol_nodes = relationship(
        "RiskControlTree",
        primaryjoin="AttackIntermediateNodes.uuid == foreign(RiskControlTree.node_uuid)",
        viewonly=True
    )

    attack_tree_nodes = relationship(
        "AttackTree",
        primaryjoin="AttackIntermediateNodes.uuid == foreign(AttackTree.node_uuid)",
        viewonly=True
    )

# ---------------------------------------------------------------------
# Technical Attack Trees - All Technical Attack trees
# ---------------------------------------------------------------------

class TechnicalTreeHome(Base):
    __tablename__ = 'technical_tree_home'

    uuid: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))   
    id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    used_in_threat: Mapped[str | None] = mapped_column(String, nullable=True)
    used_in_riskcontrol: Mapped[str | None] = mapped_column(String, nullable=True)
    toe_configuartion_id: Mapped[str | None] = mapped_column(String, nullable=True)
    assumption_id: Mapped[str | None] = mapped_column(String, nullable=True)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_by: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_on: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    version: Mapped[str] = mapped_column(String, default='3')
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    technical_heads = relationship(
        "TechnicalAttackTree",
        primaryjoin="TechnicalTreeHome.uuid == foreign(TechnicalAttackTree.node_uuid)",
        viewonly=True
    )

class TechnicalAttackTree(Base):
    """Core tree structure with polymorphic links to leaf or intermediate nodes."""
    __tablename__ = "technical_attack_tree"

    uuid: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("technical_attack_tree.uuid", ondelete="SET NULL"))
    tree_id: Mapped[str] = mapped_column(String, nullable=False)
    node_id: Mapped[str] = mapped_column(String, nullable=False)
    node_uuid: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tree_ref_uuid: Mapped[Optional[str]] = mapped_column(String, ForeignKey("attack_path_trees.uuid", ondelete="SET NULL"))
    node_type: Mapped[NodeType] = mapped_column(Enum(NodeType), nullable=False)
    gate: Mapped[Optional[str]] = mapped_column(String)
    af_value: Mapped[str] = mapped_column(String, nullable=False, default='')
    af_level: Mapped[Optional[str]] = mapped_column(String)
    highlighted: Mapped[bool] = mapped_column(Boolean, default=False)
    x: Mapped[int] = mapped_column(Integer)
    y: Mapped[int] = mapped_column(Integer)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_by: Mapped[Optional[str]] = mapped_column(String)
    updated_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[str] = mapped_column(String, default="3")
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    
    parent = relationship(
        "TechnicalAttackTree",
        remote_side="TechnicalAttackTree.uuid",
        backref="children"
    )

    reference_tree = relationship(
        "ReferenceTrees",
        back_populates="technical_attack_trees",
        foreign_keys="TechnicalAttackTree.tree_ref_uuid",  # <--- fix here
        lazy="joined"
    )

    @property
    def resolved_node(self):
        """Dynamically fetch leaf/intermediate node based on node_type."""

        match self.node_type:
            case NodeType.HEAD:
                return get_first_instance(TechnicalTreeHome, {"uuid": self.node_uuid, "is_deleted": False})
            case NodeType.LEAF:
                return get_first_instance(AttackLeafNodes, {"uuid": self.node_uuid, "is_deleted": False})
            case NodeType.INTERMEDIATE:
                return get_first_instance(AttackIntermediateNodes, {"uuid": self.node_uuid, "is_deleted": False})
            case _:
                return None

# ---------------------------------------------------------------------
# Risk Control Trees - All Risk Control trees
# ---------------------------------------------------------------------

class RiskControlTreeHome(Base):
    __tablename__ = 'riskcontrol_tree_home'

    uuid: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))   
    id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    mitigates: Mapped[str] = mapped_column(String, nullable=True)
    assumption_id: Mapped[str] = mapped_column(String, nullable=True)
    comment: Mapped[str] = mapped_column(String, nullable=True)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_on: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_by: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_on: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    version: Mapped[str] = mapped_column(String, default='3')
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    riskcontrol_heads = relationship(
        "RiskControlTree",
        primaryjoin="RiskControlTreeHome.uuid == foreign(RiskControlTree.node_uuid)",
        viewonly=True
    )

class RiskControlTree(Base):
    """Tree structure that maps to nodes in TechnicalAttackTree by UUID."""
    __tablename__ = 'riskcontrol_tree'

    uuid: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("riskcontrol_tree.uuid"), nullable=True)
    tree_ref_uuid: Mapped[Optional[str]] = mapped_column(String, ForeignKey("attack_path_trees.uuid", ondelete="SET NULL"))

    tree_id: Mapped[str] = mapped_column(String, nullable=False)
    node_id: Mapped[str] = mapped_column(String, nullable=False)
    node_uuid: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    node_type: Mapped[NodeType] = mapped_column(Enum(NodeType), nullable=False)
    gate: Mapped[str | None] = mapped_column(String, nullable=True)

    af_value: Mapped[str] = mapped_column(String, nullable=False, default='')
    af_level: Mapped[str | None] = mapped_column(String, nullable=True)
    highlighted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)

    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_on: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_by: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_on: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    version: Mapped[str] = mapped_column(String, default='3')
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    parent = relationship(
        "RiskControlTree",
        remote_side="RiskControlTree.uuid",
        backref="children"
    )

    reference_tree = relationship(
        "ReferenceTrees",
        back_populates="risk_control_trees",
        foreign_keys="RiskControlTree.tree_ref_uuid",  # <--- fix here
        lazy="joined"
    )

    @property
    def resolved_node(self, is_loading=False):
        """Resolve the node_uuid to a specific object based on node_type."""

        print(f"Resolving node {self.node_id} of type {self.node_type}")
        match self.node_type:
            case NodeType.HEAD:
                return get_first_instance(RiskControlTreeHome, {"uuid": self.node_uuid, "is_deleted": False})
            case NodeType.LEAF:
                return get_first_instance(AttackLeafNodes, {"uuid": self.node_uuid, "is_deleted": False})
            case NodeType.INTERMEDIATE:
                return get_first_instance(AttackIntermediateNodes, {"uuid": self.node_uuid, "is_deleted": False})
            case NodeType.TAT_HEAD:
                return get_first_instance(ReferenceTrees, {"uuid": self.node_uuid, "is_deleted": False})
            case _:
                return None

# ---------------------------------------------------------------------
# Attack Trees - All Attack trees
# ---------------------------------------------------------------------

class AttackTreeHome(Base):
    __tablename__ = 'attack_tree_home'

    uuid: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))   
    id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    initial_afr: Mapped[str | None] = mapped_column(String, nullable=True)
    resid_afr: Mapped[str | None] = mapped_column(String, nullable=True)
    toe_configuration_id: Mapped[str | None] = mapped_column(String, nullable=True)
    comments: Mapped[str | None] = mapped_column(String, nullable=True)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_on: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_by: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_on: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    version: Mapped[str] = mapped_column(String, default='3')
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    attack_heads = relationship(
        "AttackTree",
        primaryjoin="AttackTreeHome.uuid == foreign(AttackTree.node_uuid)",
        viewonly=True
    )

class AttackTree(Base):
    """Tree structure that maps to nodes in AttackTree by UUID."""
    __tablename__ = 'attack_tree'

    uuid: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("attack_tree.uuid"), nullable=True)
    tree_ref_uuid: Mapped[Optional[str]] = mapped_column(String, ForeignKey("attack_path_trees.uuid", ondelete="SET NULL"))

    tree_id: Mapped[str] = mapped_column(String, nullable=False)
    node_id: Mapped[str] = mapped_column(String, nullable=False)
    node_uuid: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    node_type: Mapped[NodeType] = mapped_column(Enum(NodeType), nullable=False)
    gate: Mapped[str | None] = mapped_column(String, nullable=True)

    af_value: Mapped[str] = mapped_column(String, nullable=False, default='')
    af_level: Mapped[str | None] = mapped_column(String, nullable=True)
    rf_value: Mapped[str] = mapped_column(String, nullable=False, default='')
    rf_level: Mapped[str | None] = mapped_column(String, nullable=True)
    highlighted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)

    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_on: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_by: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_on: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    version: Mapped[str] = mapped_column(String, default='3')
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    parent = relationship(
        "AttackTree",
        remote_side="AttackTree.uuid",
        backref="children"
    )

    reference_tree = relationship(
        "ReferenceTrees",
        back_populates="attack_trees",
        foreign_keys="AttackTree.tree_ref_uuid",  # <--- fix here
        lazy="joined"
    )

    @property
    def resolved_node(self):
        """Resolve the node_uuid to a specific object based on node_type."""

        match self.node_type:
            case NodeType.HEAD:
                print(get_first_instance(AttackTreeHome, {"uuid": self.node_uuid}))
                return get_first_instance(AttackTreeHome, {"uuid": self.node_uuid, "is_deleted": False})
            case NodeType.LEAF:
                return get_first_instance(AttackLeafNodes, {"uuid": self.node_uuid, "is_deleted": False})
            case NodeType.INTERMEDIATE:
                return get_first_instance(AttackIntermediateNodes, {"uuid": self.node_uuid, "is_deleted": False})
            case NodeType.TAT_HEAD:
                return get_first_instance(ReferenceTrees, {"uuid": self.node_uuid, "is_deleted": False})
            case NodeType.RCT_HEAD:
                return get_first_instance(ReferenceTrees, {"uuid": self.node_uuid, "is_deleted": False})
            case _:
                return None

# ---------------------------------------------------------------------
# Reference Trees - All Attack Paths trees reference
# ---------------------------------------------------------------------

class ReferenceTrees(Base):
    """Reference Tree details."""
    __tablename__ = "attack_path_trees"

    uuid: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_by: Mapped[Optional[str]] = mapped_column(String)
    updated_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[str] = mapped_column(String, default="3")
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    technical_attack_trees = relationship(
        "TechnicalAttackTree",
        primaryjoin=lambda: and_(
            foreign(TechnicalAttackTree.tree_ref_uuid) == ReferenceTrees.uuid,
            TechnicalAttackTree.is_deleted == False
        ),
        lazy="subquery",
        back_populates="reference_tree",
        cascade="all, delete-orphan"
    )

    risk_control_trees = relationship(
        "RiskControlTree",
        primaryjoin=lambda: and_(
            foreign(RiskControlTree.tree_ref_uuid) == ReferenceTrees.uuid,
            RiskControlTree.is_deleted == False
        ),
        lazy="subquery",
        back_populates="reference_tree",
        cascade="all, delete-orphan"
    )

    attack_trees = relationship(
        "AttackTree",
        primaryjoin=lambda: and_(
            foreign(AttackTree.tree_ref_uuid) == ReferenceTrees.uuid,
            AttackTree.is_deleted == False
        ),
        lazy="subquery",
        back_populates="reference_tree",
        cascade="all, delete-orphan"
    )

