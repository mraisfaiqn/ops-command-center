from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db, Base
import models
import schemas
from ai_service import generate_incident_report

# Creates tables if they don't exist yet (fine for a one-day prototype;
# use Alembic migrations if this ever goes beyond a demo)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ops Command Center API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------- Assets ----------

@app.post("/assets", response_model=schemas.AssetOut)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(get_db)):
    db_asset = models.Asset(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@app.get("/assets", response_model=List[schemas.AssetOut])
def list_assets(db: Session = Depends(get_db)):
    return db.query(models.Asset).all()


@app.get("/assets/{asset_id}", response_model=schemas.AssetOut)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


# ---------- Incidents ----------

@app.post("/incidents", response_model=schemas.IncidentOut)
def create_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == incident.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    db_incident = models.Incident(**incident.model_dump())
    db.add(db_incident)

    # Reflect the incident on the asset's status
    asset.status = models.AssetStatus.down if incident.severity in (
        models.Severity.high, models.Severity.critical
    ) else models.AssetStatus.degraded

    db.commit()
    db.refresh(db_incident)
    return db_incident


@app.get("/incidents", response_model=List[schemas.IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(models.Incident).order_by(models.Incident.start_time.desc()).all()


@app.get("/incidents/{incident_id}", response_model=schemas.IncidentOut)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


# ---------- Incident Reports (AI generation wired up in the next step) ----------

@app.get("/incidents/{incident_id}/report", response_model=schemas.IncidentReportOut)
def get_incident_report(incident_id: str, db: Session = Depends(get_db)):
    report = db.query(models.IncidentReport).filter(
        models.IncidentReport.incident_id == incident_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="No report generated yet for this incident")
    return report


@app.post("/incidents/{incident_id}/generate-report", response_model=schemas.IncidentReportOut)
def create_incident_report(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    asset = db.query(models.Asset).filter(models.Asset.id == incident.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset linked to this incident not found")

    try:
        ai_output = generate_incident_report(asset, incident)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI report generation failed: {str(e)}")

    # Regenerating replaces any existing report for this incident
    existing = db.query(models.IncidentReport).filter(
        models.IncidentReport.incident_id == incident_id
    ).first()
    if existing:
        db.delete(existing)
        db.commit()

    report = models.IncidentReport(
        incident_id=incident_id,
        ai_summary=ai_output["summary"],
        root_cause_hypothesis=ai_output["root_cause_hypothesis"],
        stakeholder_email_draft=ai_output["stakeholder_email_draft"],
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report