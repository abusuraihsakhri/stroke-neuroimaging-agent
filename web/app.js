"use strict";

// Entirely local, illustrative thresholds matching agents/workers.py.
// No image analysis, clinical interpretation, external API, or audit signing is performed.
const PRIMARY_DEMO_LIMIT = 25;
const SECONDARY_DEMO_LIMIT = 12;
let evaluated = 0;
let totalAlerts = 0;
let latestResult = null;

const element = (id) => document.getElementById(id);

function auditDemo() {
    const caseId = element("task_id").value.trim();
    const target = element("target_id").value.trim();
    const primaryText = element("primary_metric").value.trim();
    const secondaryText = element("secondary_metric").value.trim();
    const primary = Number(primaryText);
    const secondary = Number(secondaryText);
    const status = element("status_descriptor").value.trim();
    const isCritical = element("is_critical").checked;

    if (!caseId || !target || !status ||
        !primaryText || !secondaryText ||
        !Number.isFinite(primary) || !Number.isFinite(secondary) ||
        primary < 0 || secondary < 0) {
        throw new Error("Enter identifiers, a status, and finite non-negative numeric values.");
    }

    const alerts = [];
    if (primary > PRIMARY_DEMO_LIMIT) {
        alerts.push({
            worker: "InvariantQCWorker",
            urgency: "ELEVATED_RISK",
            finding: "Synthetic primary threshold exceeded (25)."
        });
    }
    if (isCritical || secondary > SECONDARY_DEMO_LIMIT) {
        alerts.push({
            worker: "SafetyEscalationWorker",
            urgency: isCritical ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
            finding: "Synthetic priority flag or secondary threshold (12) triggered."
        });
    }
    if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"]
        .some((token) => status.toUpperCase().includes(token))) {
        alerts.push({
            worker: "ProtocolConformanceWorker",
            urgency: "ELEVATED_RISK",
            finding: "Synthetic status-discrepancy keyword detected."
        });
    }
    const critical = alerts.some((a) => a.urgency === "CRITICAL_STAT_PANIC");
    return {
        mode: "LOCAL_SYNTHETIC_DEMO",
        not_for_clinical_use: true,
        task_id: caseId,
        target_identifier: target,
        inputs: {
            primary_metric: primary,
            secondary_metric: secondary,
            status_descriptor: status,
            is_critical_flag: isCritical
        },
        overall_urgency: critical ? "CRITICAL_STAT_PANIC" : (alerts.length ? "ELEVATED_RISK" : "ROUTINE"),
        total_alerts: alerts.length,
        alerts: alerts,
        notice: "Demonstration only: not ASPECTS scoring, LVO detection, treatment triage, or a signed audit."
    };
}

function runAudit() {
    try {
        latestResult = auditDemo();
        evaluated += 1;
        totalAlerts += latestResult.total_alerts;
        element("m-tasks").textContent = String(evaluated);
        element("m-audit").textContent = String(totalAlerts);
        element("m-status").textContent = "DEMO";
        element("outputConsole").textContent = JSON.stringify(latestResult, null, 2);
        element("download-btn").disabled = false;
    } catch (error) {
        latestResult = null;
        element("download-btn").disabled = true;
        element("outputConsole").textContent = "Input error: " + error.message;
    }
}

function downloadResult() {
    if (!latestResult) return;
    const blob = new Blob([JSON.stringify(latestResult, null, 2) + "\n"], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "stroke-synthetic-demo.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}

document.addEventListener("DOMContentLoaded", () => {
    element("run-btn").addEventListener("click", runAudit);
    element("download-btn").addEventListener("click", downloadResult);
});
