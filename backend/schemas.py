from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from models import AssetType, AssetStatus, Severity


# ---------- Asset ----------

class AssetBase(BaseModel):
    name: str
    asset_type: AssetType
    location: Optional[str] = None
    status: AssetStatus = AssetStatus.healthy


class AssetCreate(AssetBase):
    pass


class AssetOut(AssetBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Incident ----------

class IncidentBase(BaseModel):
    asset_id: str
    severity: Severity
    description: str
    start_time: datetime
    end_time: Optional[datetime] = None


class IncidentCreate(IncidentBase):
    pass


class IncidentOut(IncidentBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Incident Report ----------

class IncidentReportOut(BaseModel):
    id: str
    incident_id: str
    ai_summary: Optional[str]
    root_cause_hypothesis: Optional[str]
    stakeholder_email_draft: Optional[str]
    generated_at: datetime

    class Config:
        from_attributes = True
