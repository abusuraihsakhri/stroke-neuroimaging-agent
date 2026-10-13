# Stroke Neuroimaging Agent

A **synthetic rule-evaluation demonstration** with a Python CLI, FastAPI service, and static browser interface. The code evaluates illustrative numeric thresholds and status flags. **It does not read CT/MRI images, compute ASPECTS, identify large-vessel occlusions, estimate treatment eligibility, or provide clinical decision support.** Clinical validation has not been performed.

## Browser demo

Open `web/index.html` in a modern browser. Enter **synthetic** identifiers and numeric values, select **Evaluate Synthetic Case**, and optionally download the resulting JSON.

The browser executes local JavaScript. It makes no API calls, requires no Python or WebAssembly, does not persist entered data, and does **not** create an HMAC-signed audit trail. No patient information should be entered. GitHub Pages deployment is configured via `.github/workflows/pages.yml`; an unverified deployment is not presented as a working link.

The demonstration implements these **arbitrary, nonclinical** rules:

- Primary metric greater than 25: elevated flag.
- Secondary metric greater than 12: elevated flag; an explicit priority flag produces a critical demo flag.
- Status containing DISCORDANT, ANOMALY, MUTANT, VIOLATION, FAIL, or REJECT: discrepancy flag.

These rules have no claimed relationship to validated stroke-imaging algorithms.

## Install and run

Requires Python 3.10 or later.

```bash
python -m pip install -e ".[api,test]"
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
python cli.py audit --task-id SYN-001 --target CASE-001 --primary 29 --secondary 4 --status NOMINAL
python cli.py batch -i input.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The primary CSV interface uses `task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag` headers. Use explicit `true` or `false` values for the critical flag. Numeric metrics must be finite and non-negative. Downloaded CSV outputs escape spreadsheet formula-like user input.

Use `python stroke_neuroimaging_agent_app.py --help` or `python stroke_sentinel_app.py --help` for the preserved legacy interfaces. They use different input schemas and are retained for compatibility. `enrichment.py` contains generic threshold-based demonstration modules, **not implemented clinical FHIR integration or imaging analysis**.

## REST API

The server started by `python cli.py serve` is `agents.api:app`. It exposes:

| Endpoint | Function |
| --- | --- |
| `GET /health` | Service health |
| `GET /metrics` | In-memory counters in JSON |
| `POST /api/audit` | Synthetic rule evaluation |
| `POST /api/chat` | Deterministic mock reply; no external LLM |
| `GET /api/audit/logs` | Audit history; requires `AUDIT_LOGS_API_KEY` and matching `X-Audit-Key` header |

`AUDIT_SECRET_KEY` is required for Python evaluations; it must be a unique secret of at least 32 characters. Audit entries use an in-memory HMAC-SHA256 hash chain that is checked by recomputing signatures. The history is lost on process restart. The record is **not** an immutable, externally anchored, or regulatory-compliant audit system. The regex-based identifier guard recognizes some common patterns but is **not a validated de-identification method**. Do not submit real patient data.

The audit and chat endpoints have no account authentication; do not bind the API to an untrusted network. The supplied Docker Compose configuration binds to localhost and requires you to provide a secret:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
docker compose up --build
```

## Testing

```bash
python -m pytest -q
python -m pip check
node --check web/app.js
node tests/web_smoke.cjs
```

CI covers Python 3.10–3.12, package installation, dependency checks, regression tests, and browser JavaScript smoke tests. The web demo targets current desktop/mobile browsers supporting modern ECMAScript and Blob downloads.

## Privacy and security

Browser calculations run only in the current tab, without remote requests or local-storage writes. The Python API processes and temporarily retains submitted identifiers and results in process memory, so **synthetic inputs only** are appropriate. API audit history is access-key protected but is not a substitute for authentication, production-grade encryption or an approved clinical data pipeline.

## License

MIT; see [LICENSE](LICENSE).
