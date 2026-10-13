"""Regression tests for audit integrity, exports and API access."""
import csv
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agents.base import AuditTrail, SecurityException, AuditLogger
from agents.api import app
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from cli import main, parse_csv_bool


KEY = "development-test-key-not-for-any-production-use"


def test_audit_recomputes_mac_after_tampering():
    trail = AuditTrail(secret_key=KEY)
    trail.log("operator", "user", "EVALUATE", {"case": "SYN-1"})
    trail.log("operator", "user", "EVALUATE", {"case": "SYN-2"})
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "attacker"
    assert not trail.verify_integrity()


def test_audit_rejects_modified_terminal_signature():
    trail = AuditTrail(secret_key=KEY)
    trail.log("worker", "user", "EVALUATE", {"case": "SYN-1"})
    trail.logs[-1]["current_hash"] = "f" * 64
    assert not trail.verify_integrity()


def test_audit_get_trail_returns_snapshot():
    trail = AuditTrail(secret_key=KEY)
    trail.log("worker", "user", "EVALUATE", {"case": "SYN-1"})
    trail.get_trail()[0]["actor"] = "attacker"
    assert trail.verify_integrity()


@pytest.mark.parametrize("value,expected", [
    ("False", False), ("FALSE", False), ("0", False),
    ("true", True), ("YES", True), ("1", True), ("", False)
])
def test_csv_boolean_parse(value, expected):
    assert parse_csv_bool(value) is expected


def test_csv_boolean_invalid():
    with pytest.raises(ValueError):
        parse_csv_bool("sometimes")


def test_csv_batch_uses_explicit_false_and_escapes_formulas(tmp_path: Path):
    source = tmp_path / "case.csv"
    target = tmp_path / "results.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "task_id", "target_identifier", "primary_metric",
            "secondary_metric", "status_descriptor", "is_critical_flag",
        ])
        writer.writeheader()
        writer.writerow({
            "task_id": "=1+1", "target_identifier": "SYN-1",
            "primary_metric": 2, "secondary_metric": 3,
            "status_descriptor": "NOMINAL", "is_critical_flag": "False",
        })
    assert main(["batch", "-i", str(source), "-o", str(target)]) == 0
    with target.open(newline="", encoding="utf-8") as handle:
        result = next(csv.DictReader(handle))
    assert result["overall_urgency"] == "ROUTINE"
    assert result["task_id"] == "'=1+1"


def test_payload_attributes_are_checked_for_identifiers():
    supervisor = SystemSupervisor()
    with pytest.raises(SecurityException):
        supervisor.process_task(SystemTaskPayload(
            task_id="T1", target_identifier="SYN-1",
            primary_metric=1.0, attributes={"notes": "MRN-123456"}
        ))


def test_audit_logs_denied_without_separate_key(monkeypatch):
    monkeypatch.delenv("AUDIT_LOGS_API_KEY", raising=False)
    with TestClient(app) as client:
        assert client.get("/api/audit/logs").status_code == 403


def test_audit_logs_accept_configured_key(monkeypatch):
    monkeypatch.setenv("AUDIT_LOGS_API_KEY", "a-dedicated-development-audit-access-key")
    with TestClient(app) as client:
        response = client.get("/api/audit/logs", headers={
            "X-Audit-Key": "a-dedicated-development-audit-access-key"
        })
        assert response.status_code == 200
        assert response.json()["verified"] is True


def test_api_rejects_recognizable_identifiers():
    with TestClient(app) as client:
        response = client.post("/api/audit", json={
            "task_id": "T-1", "target_identifier": "SYN-1",
            "primary_metric": 1, "attributes": {"private": "MRN-123456"}
        })
        assert response.status_code == 422
        assert "MRN" not in response.text
