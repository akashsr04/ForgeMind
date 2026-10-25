import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    UniqueConstraint,
    Text,
)
from sqlalchemy.orm import relationship
from app.infrastructure.db.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(100), nullable=False)  # e.g., motor, pump, conveyor, cnc
    location = Column(String(255), nullable=True)
    criticality = Column(Float, nullable=False, default=1.0)  # e.g., 1.0 to 5.0
    status = Column(String(50), nullable=False, default="operational")  # operational, degraded, offline, maintenance
    metadata_json = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    outgoing_edges = relationship(
        "AssetEdge",
        foreign_keys="AssetEdge.source_asset_id",
        back_populates="source_asset",
        cascade="all, delete-orphan",
    )
    incoming_edges = relationship(
        "AssetEdge",
        foreign_keys="AssetEdge.target_asset_id",
        back_populates="target_asset",
        cascade="all, delete-orphan",
    )
    telemetry_readings = relationship(
        "TelemetryReading",
        back_populates="asset",
        cascade="all, delete-orphan",
    )
    incidents = relationship(
        "Incident",
        back_populates="asset",
        cascade="all, delete-orphan",
    )


class AssetEdge(Base):
    __tablename__ = "asset_edges"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_asset_id = Column(String(36), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    target_asset_id = Column(String(36), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(100), nullable=False)  # feeds, drives, depends_on, located_near
    weight = Column(Float, nullable=False, default=1.0)
    metadata_json = Column(JSON, nullable=True, default=dict)

    source_asset = relationship("Asset", foreign_keys=[source_asset_id], back_populates="outgoing_edges")
    target_asset = relationship("Asset", foreign_keys=[target_asset_id], back_populates="incoming_edges")

    __table_args__ = (
        UniqueConstraint("source_asset_id", "target_asset_id", "relationship_type", name="uq_asset_edge"),
    )


class TelemetryReading(Base):
    __tablename__ = "telemetry_readings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    asset_id = Column(String(36), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    sensor_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    observed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    source = Column(String(100), default="synthetic_sensor", nullable=False)

    asset = relationship("Asset", back_populates="telemetry_readings")

    __table_args__ = (
        Index("ix_telemetry_asset_observed", "asset_id", "observed_at"),
        Index("ix_telemetry_sensor_observed", "sensor_name", "observed_at"),
    )


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    asset_id = Column(String(36), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(50), default="medium", nullable=False)  # low, medium, high, critical
    status = Column(String(50), default="open", nullable=False)  # open, investigating, mitigated, resolved
    trigger_type = Column(String(100), default="telemetry_anomaly", nullable=False)
    detected_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    context_json = Column(JSON, nullable=True, default=dict)
    is_synthetic = Column(Boolean, default=True, nullable=False)

    asset = relationship("Asset", back_populates="incidents")
    investigations = relationship("Investigation", back_populates="incident", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="incident")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False)  # procedure, manual, checklist, spec
    asset_type = Column(String(100), nullable=False)
    source_label = Column(String(255), nullable=False)
    version = Column(String(50), default="1.0", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    is_demo = Column(Boolean, default=True, nullable=False)


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="completed", nullable=False)  # running, completed, failed
    workflow_version = Column(String(50), default="1.0.0", nullable=False)
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    summary = Column(Text, nullable=True)
    structured_result = Column(JSON, nullable=True, default=dict)
    error_code = Column(String(100), nullable=True)

    incident = relationship("Incident", back_populates="investigations")
    recommendations = relationship("Recommendation", back_populates="investigation", cascade="all, delete-orphan")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(100), nullable=False)  # inspect, derate, repair, replace, monitor
    title = Column(String(255), nullable=False)
    rationale = Column(Text, nullable=True)
    score = Column(Float, nullable=False, default=0.0)
    score_components = Column(JSON, nullable=True, default=dict)
    uncertainty_summary = Column(JSON, nullable=True, default=dict)
    evidence_refs = Column(JSON, nullable=True, default=list)
    is_advisory = Column(Boolean, default=True, nullable=False)

    investigation = relationship("Investigation", back_populates="recommendations")


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    scenario_type = Column(String(100), nullable=False)  # outage, derating, inspection, repair
    parameters = Column(JSON, nullable=False, default=dict)
    baseline_result = Column(JSON, nullable=False, default=dict)
    scenario_result = Column(JSON, nullable=False, default=dict)
    assumptions = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    is_synthetic = Column(Boolean, default=True, nullable=False)

    incident = relationship("Incident", back_populates="simulations")
