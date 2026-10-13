const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const fields = {
    task_id: {value: "SYN-1"},
    target_id: {value: "CASE-01"},
    primary_metric: {value: "29.4"},
    secondary_metric: {value: "14.8"},
    status_descriptor: {value: "DISCORDANT"},
    is_critical: {checked: true},
    "m-tasks": {textContent: "0"},
    "m-audit": {textContent: "0"},
    "m-status": {textContent: "DEMO"},
    outputConsole: {textContent: ""},
    "run-btn": {addEventListener: () => {}},
    "download-btn": {addEventListener: () => {}, disabled: true}
};
const sandbox = {
    document: {
        getElementById: (id) => fields[id],
        addEventListener: (event, handler) => {
            if (event === "DOMContentLoaded") handler();
        }
    },
    Number, JSON, String, Error
};
vm.runInNewContext(fs.readFileSync("web/app.js", "utf8"), sandbox, {filename: "web/app.js"});

sandbox.runAudit();
let result = JSON.parse(fields.outputConsole.textContent);
assert.equal(result.mode, "LOCAL_SYNTHETIC_DEMO");
assert.equal(result.overall_urgency, "CRITICAL_STAT_PANIC");
assert.equal(result.total_alerts, 3);
assert.equal(fields["m-tasks"].textContent, "1");
assert.equal(fields["m-audit"].textContent, "3");
assert.equal(fields["download-btn"].disabled, false);
assert.ok(!("audit_hash" in result));

fields.primary_metric.value = "";
sandbox.runAudit();
assert.match(fields.outputConsole.textContent, /Input error/);
assert.equal(fields["m-tasks"].textContent, "1");

fields.primary_metric.value = "2";
fields.secondary_metric.value = "3";
fields.status_descriptor.value = "NOMINAL";
fields.is_critical.checked = false;
sandbox.runAudit();
result = JSON.parse(fields.outputConsole.textContent);
assert.equal(result.overall_urgency, "ROUTINE");
assert.equal(result.total_alerts, 0);

console.log("Static browser demonstration smoke test passed.");
