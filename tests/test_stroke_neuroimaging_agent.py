"""
Automated Pytest Test Suite for Stroke Neuroimaging Agent.
Domain: Radiology & Neuroimaging Systems
Standard: ACR RADS / Fleischner Society / ASPECTS Guidelines
"""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


# ==============================================================================
# Input Validation Tests
# ==============================================================================

def test_payload_rejects_nan_primary():
    """NaN metric values must be rejected."""
    with pytest.raises(Exception):  # ValidationError
        SystemTaskPayload(task_id="T-NAN", target_identifier="KEY-01", primary_metric=math.nan)


def test_payload_rejects_nan_secondary():
    """NaN secondary metric values must be rejected."""
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="T-NAN2", target_identifier="KEY-01", primary_metric=10.0, secondary_metric=math.nan)


def test_payload_rejects_inf_primary():
    """Infinite metric values must be rejected."""
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="T-INF", target_identifier="KEY-01", primary_metric=math.inf)


def test_payload_rejects_negative_primary():
    """Negative metric values must be rejected."""
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="T-NEG", target_identifier="KEY-01", primary_metric=-5.0)


def test_payload_rejects_empty_task_id():
    """Empty task_id must be rejected."""
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="   ", target_identifier="KEY-01", primary_metric=10.0)


def test_payload_rejects_empty_target():
    """Empty target_identifier must be rejected."""
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="T1", target_identifier="", primary_metric=10.0)


def test_payload_accepts_valid_zero_metrics():
    """Zero metric values are valid (boundary case)."""
    p = SystemTaskPayload(task_id="T-ZERO", target_identifier="KEY-01", primary_metric=0.0, secondary_metric=0.0)
    assert p.primary_metric == 0.0
    assert p.secondary_metric == 0.0


# ==============================================================================
# Audit Security Tests
# ==============================================================================

def test_audit_trail_requires_secret_key():
    """AuditTrail must require a secret key."""
    import os
    original = os.environ.get("AUDIT_SECRET_KEY")
    try:
        del os.environ["AUDIT_SECRET_KEY"]
        with pytest.raises(SecurityException):
            AuditTrail(secret_key="")
    finally:
        if original is not None:
            os.environ["AUDIT_SECRET_KEY"] = original


def test_audit_trail_rejects_short_key():
    """AuditTrail must reject keys shorter than 32 characters."""
    with pytest.raises(SecurityException):
        AuditTrail(secret_key="short-key")


def test_audit_trail_accepts_valid_key():
    """AuditTrail accepts a key of sufficient length."""
    trail = AuditTrail(secret_key="this-is-a-valid-32-char-secret-key!!")
    assert trail.secret_key == b"this-is-a-valid-32-char-secret-key!!"
