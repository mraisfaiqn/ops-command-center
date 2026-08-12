import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


def gen_uuid():
    return str(uuid.uuid4())


class AssetType(str, enum.Enum):
    server = "server"
    network_device = "network_device"
    storage = "storage"
    other = "other"


class AssetStatus(str, enum.Enum):
    healthy = "healthy"
    degraded = "degraded"
    down = "down"


class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    asset_type = Column(SAEnum(AssetType), nullable=False)
    location = Column(String, nullable=True)
    status = Column(SAEnum(AssetStatus), nullable=False, default=AssetStatus.healthy)
    created_at = Column(DateTime, default=datetime.utcnow)

    incidents = relationship("Incident", back_populates="asset", cascade="all, delete-orphan")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    asset_id = Column(UUID(as_uuid=False), ForeignKey("assets.id"), nullable=False)
    severity = Column(SAEnum(Severity), nullable=False)
    description = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="incidents")
    report = relationship("IncidentReport", back_populates="incident", uselist=False, cascade="all, delete-orphan")


class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    incident_id = Column(UUID(as_uuid=False), ForeignKey("incidents.id"), nullable=False, unique=True)
    ai_summary = Column(Text, nullable=True)
    root_cause_hypothesis = Column(Text, nullable=True)
    stakeholder_email_draft = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="report")
