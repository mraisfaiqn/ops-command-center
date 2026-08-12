"""
Seed script for the Ops Command Center demo.

Generates a synthetic asset inventory (servers, network devices, storage)
and a batch of simulated incidents spread across the last ~30 days, so the
dashboard has realistic-looking data to demonstrate the AI report
generation and trend views.

Run with:
    python seed_data.py

Safe to re-run — it clears existing data first so you don't end up with
duplicates across multiple runs.
"""

import random
from datetime import datetime, timedelta

from database import SessionLocal, engine, Base
import models

random.seed(42)  # reproducible demo data

Base.metadata.create_all(bind=engine)

# ---------- Synthetic asset inventory ----------

ASSETS = [
    ("PROD-WEB-01", models.AssetType.server, "KL Data Center - Rack A3"),
    ("PROD-WEB-02", models.AssetType.server, "KL Data Center - Rack A3"),
    ("PROD-DB-01", models.AssetType.server, "KL Data Center - Rack A5"),
    ("PROD-DB-02-REPLICA", models.AssetType.server, "KL Data Center - Rack A5"),
    ("APP-SVR-EAST-01", models.AssetType.server, "Penang DR Site - Rack B1"),
    ("CORE-SWITCH-01", models.AssetType.network_device, "KL Data Center - Network Room"),
    ("CORE-SWITCH-02", models.AssetType.network_device, "KL Data Center - Network Room"),
    ("EDGE-ROUTER-KL", models.AssetType.network_device, "KL Data Center - Network Room"),
    ("EDGE-ROUTER-PG", models.AssetType.network_device, "Penang DR Site - Network Room"),
    ("FIREWALL-PRIMARY", models.AssetType.network_device, "KL Data Center - Network Room"),
    ("SAN-STORAGE-01", models.AssetType.storage, "KL Data Center - Rack A7"),
    ("BACKUP-NAS-01", models.AssetType.storage, "Penang DR Site - Rack B2"),
]

# ---------- Simulated incident templates ----------

INCIDENT_TEMPLATES = [
    (models.Severity.critical, "Complete service outage - asset unreachable via ping and SNMP"),
    (models.Severity.high, "Sustained high latency (>500ms) affecting downstream services"),
    (models.Severity.high, "Repeated connection timeouts reported by dependent applications"),
    (models.Severity.medium, "CPU utilization sustained above 90% for over 20 minutes"),
    (models.Severity.medium, "Disk usage crossed 85% warning threshold"),
    (models.Severity.medium, "Intermittent packet loss detected on primary uplink"),
    (models.Severity.low, "Minor configuration drift detected during routine audit"),
    (models.Severity.low, "Non-critical service restart required after failed health check"),
]


def seed():
    db = SessionLocal()
    try:
        # Clear existing data (children first due to FK constraints)
        db.query(models.IncidentReport).delete()
        db.query(models.Incident).delete()
        db.query(models.Asset).delete()
        db.commit()

        asset_objs = []
        for name, asset_type, location in ASSETS:
            asset = models.Asset(
                name=name,
                asset_type=asset_type,
                location=location,
                status=models.AssetStatus.healthy,
            )
            db.add(asset)
            asset_objs.append(asset)
        db.commit()
        for a in asset_objs:
            db.refresh(a)

        # Generate 15-20 incidents spread across the last 30 days
        num_incidents = random.randint(15, 20)
        now = datetime.utcnow()

        for _ in range(num_incidents):
            asset = random.choice(asset_objs)
            severity, description = random.choice(INCIDENT_TEMPLATES)

            days_ago = random.uniform(0, 30)
            start_time = now - timedelta(days=days_ago)

            # Higher severity incidents tend to take longer to resolve
            duration_minutes = {
                models.Severity.critical: random.uniform(45, 180),
                models.Severity.high: random.uniform(20, 90),
                models.Severity.medium: random.uniform(10, 45),
                models.Severity.low: random.uniform(5, 20),
            }[severity]

            # ~10% of incidents are still ongoing (no end_time)
            is_ongoing = random.random() < 0.1
            end_time = None if is_ongoing else start_time + timedelta(minutes=duration_minutes)

            incident = models.Incident(
                asset_id=asset.id,
                severity=severity,
                description=f"{description} on {asset.name}.",
                start_time=start_time,
                end_time=end_time,
            )
            db.add(incident)

            # Reflect status on the asset for any incident in the last 24h
            if days_ago < 1:
                asset.status = (
                    models.AssetStatus.down
                    if severity in (models.Severity.critical, models.Severity.high)
                    else models.AssetStatus.degraded
                )

        db.commit()
        print(f"Seeded {len(asset_objs)} assets and {num_incidents} incidents.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
