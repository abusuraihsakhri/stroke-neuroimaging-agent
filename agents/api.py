"""
FastAPI REST API Server for Stroke Neuroimaging Agent.
"""
import os
import hmac
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Header
from .base import SecurityException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Stroke Neuroimaging Agent API",
    description="Synthetic rule-evaluation demonstration. Not validated for medical decision-making.",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "stroke-neuroimaging-agent", "mode": "synthetic_demonstration", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a recognizable personal identifier.")
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a recognizable personal identifier.")


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_key: str = Header(default="")):
    """Audit history is private unless explicitly enabled with a separate access key."""
    configured = os.getenv("AUDIT_LOGS_API_KEY", "")
    if not configured or not hmac.compare_digest(x_audit_key, configured):
        raise HTTPException(status_code=403, detail="Audit logs access not configured or denied.")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
