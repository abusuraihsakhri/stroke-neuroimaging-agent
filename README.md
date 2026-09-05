# Stroke Neuroimaging Agent

> **Domain:** Diagnostic Radiology & Medical Imaging AI
> **Reference Guidelines & Standards:** `American College of Radiology (ACR) RADS & Fleischner Society`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Stroke Neuroimaging Agent** is an advanced analytical and computational platform implementing ASPECTS Score (0-10) & Large Vessel Occlusion (LVO) Thrombectomy Triager.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`ASPECTSScorerAgent`**: Specialized Sub-Agent 1 for stroke-neuroimaging-agent
- **`LVOOcclusionFinderAgent`**: Specialized Sub-Agent 2 for stroke-neuroimaging-agent
- **`ThrombolysisWindowTimerAgent`**: Specialized Sub-Agent 3 for stroke-neuroimaging-agent

---

## 💻 CLI Quickstart & Usage

### Installation

```bash
pip install fastapi uvicorn pydantic pytest
```

### Configuration

Set the required audit secret key (minimum 32 characters):

```bash
export AUDIT_SECRET_KEY="your-secure-production-audit-key-minimum-32-chars"
```

### 1. Guided Interactive Mode
```bash
python cli.py audit
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py audit --task-id <value> --target <value> --primary <value> --secondary <value>
```

### 3. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Flag | Description | Default |
|:-----|:------------|:--------|
| `--task-id` | Unique task / case identifier | `TASK-2026-001` |
| `--target` | Entity or target identifier | `KEY-TARGET-01` |
| `--primary` | Primary domain measurement (float) | `28.5` |
| `--secondary` | Secondary kinetic/confidence score (float) | `14.2` |
| `--critical` | Emergency escalation flag | `False` |
| `--status` | Status code or phenotype descriptor | `DISCORDANT` |
| `-i, --input` | Input CSV file path (batch mode) | *required* |
| `-o, --output` | Output CSV file path (batch mode) | `results.csv` |

### Input Data Schema (batch CSV)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Entity or target identifier | Required |
| `primary_metric` | Primary measurement (float, non-negative) | Required |
| `secondary_metric` | Secondary score (float, non-negative) | Required |
| `is_critical_flag` | Emergency escalation flag | Required |
| `status_descriptor` | Status code or phenotype descriptor | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition. Requires `AUDIT_SECRET_KEY` environment variable (minimum 32 characters).
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).
* **Input Validation:** Pydantic v2 validators reject NaN, Inf, and negative metric values.

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t stroke-neuroimaging-agent .
docker run -e AUDIT_SECRET_KEY="your-secure-production-key" -p 8000:8000 stroke-neuroimaging-agent
```

Or using Docker Compose:

```bash
docker-compose up -d
```

---

## 📁 Project Structure

```
stroke-neuroimaging-agent/
├── agents/                  # Core agent modules
│   ├── __init__.py          # Package init
│   ├── api.py               # FastAPI REST API server
│   ├── base.py              # Security, PHI Guard, HMAC-SHA256 Audit Trail
│   ├── learning.py          # Bayesian Calibration Engine
│   ├── llm_factory.py       # LLM provider factory
│   ├── metrics.py           # Prometheus metrics collector
│   ├── models.py            # Pydantic v2 data models
│   ├── streamer.py          # WebSocket telemetry streamer
│   ├── supervisor.py        # System Supervisor orchestrator
│   └── workers.py           # Specialized domain workers
├── tests/                   # Test suite
│   ├── test_enrichment.py   # Enrichment module tests
│   └── test_stroke_neuroimaging_agent.py  # Core module tests
├── cli.py                   # Main CLI entry point
├── conftest.py              # Pytest configuration
├── enrichment.py            # Feature enrichment modules
├── simulator.py             # High-throughput simulation
├── stroke_sentinel.py       # Standalone stroke sentinel agent
├── stroke_neuroimaging_agent_app.py  # Alt entry point
└── stroke_neuroimaging_agent/  # Alternative package structure
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
