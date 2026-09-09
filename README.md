# Recollect — Cognitive Wellness & Connection Platform

**Recollect** is a multimodal conversational companion and cognitive wellness observation platform designed for older adults and their families. It pairs empathetic dialogue and reminiscence prompts with clinical cognitive observation models and caregiver insight windows.

---

## 🏗️ Architecture Overview

The repository is organized into distinct, modular tiers:

```text
├── frontend/             # Web & Mobile UI (HTML5, CSS3, ES Modules, Speech & Audio subsystem)
├── backend/              # Python FastAPI backend (Hexagonal architecture: Core, Ports, Adapters)
│   ├── src/recollect/    # Domain core, application use-cases, and API routes
│   ├── tests/            # Test suite (Unit, API, Architecture dependency invariants)
│   ├── pyproject.toml    # Python dependencies (uv-managed)
│   └── Dockerfile        # Production multi-stage Docker container
├── database/             # Relational persistence & migrations
│   ├── alembic.ini       # Alembic migration configuration
│   ├── migrations/       # Schema versions and environment runners
│   └── docker-compose.yml# Local PostgreSQL service container
├── docs/                 # Project documentation & design hub
│   ├── architecture/     # Architecture spine, ADRs, and review audits
│   ├── specs/            # Technical specifications & protocols
│   ├── prds/             # Product Requirements Documents
│   ├── forge/            # Product discovery reports & ideation
│   ├── design/           # UI/UX design specifications & assets
│   └── epics.md          # Implementation epics & stories
├── ios/                  # Native iOS application wrapper (Capacitor)
├── api/                  # Serverless entrypoint (Vercel)
└── scripts/              # Local development tooling & preview servers
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Node.js**: `v22+`
- **Python**: `3.13+` with [`uv`](https://docs.astral.sh/uv/) installed

### 2. Running the Full Stack Locally

#### Backend (FastAPI API)
```bash
# Start backend API on http://127.0.0.1:8000
npm run dev:backend
# or directly with uv:
uv run --directory backend uvicorn recollect.edge.api.main:app --reload --port 8000
```

#### Frontend & Local Proxy Server
```bash
# Start local preview on http://127.0.0.1:3000 (proxies /v1 and /api to backend)
npm run dev
```

Open [http://127.0.0.1:3000](http://127.0.0.1:3000) in your browser.

---

## 🧪 Testing & Validation

### Run Backend Tests (179 Automated Invariant & Unit Tests)
```bash
npm run test:backend
# or directly with uv:
uv run --directory backend pytest
```

### Run Frontend & Script Syntax Checks
```bash
npm run check
```

---

## 📱 Mobile App (iOS)

The mobile client is packaged as a native iOS app using Capacitor:

1. **Install dependencies**:
   ```bash
   npm ci
   ```
2. **Synchronize web assets to Xcode project**:
   ```bash
   npm run ios:sync
   ```
3. **Open project in Xcode**:
   ```bash
   npm run ios:open
   ```

In Xcode, select the **App** scheme and an iPhone simulator / connected device, then press **Run**.

---

## 🗄️ Database & Migrations

The backend defaults to SQLite for local zero-config development, and supports PostgreSQL for production deployments.

- **Start local PostgreSQL container**:
  ```bash
  docker compose -f database/docker-compose.yml up -d
  ```

- **Run schema migrations**:
  ```bash
  uv run --directory backend alembic -c database/alembic.ini upgrade head
  ```

See [database/README.md](file:///c:/Users/braed/OneDrive/Desktop/VIBEFORGOOD/database/README.md) for full details.

---

## 🔒 Privacy & Clinical Ethics Boundaries

- **Observations, Not Diagnoses**: Recollect produces structured clinical observation signals (prosody, latency, memory recall, orientation) to aid families and clinicians; it does not issue automated medical diagnoses.
- **Explicit Consent & Sovereign Key Storage**: Senior consent is revocable at any time. Data is protected with cryptographic isolation.
- **Egress Guardrails**: Audio streams and raw transcripts never leave local boundaries without explicit data grants.
