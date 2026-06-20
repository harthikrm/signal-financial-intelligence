# Signal Financial Intelligence

**Signal** is a full-stack financial intelligence platform for a curated universe of **70 US public companies**. It ingests SEC filings and market data, transforms metrics with dbt, computes investment signals, and serves them through a FastAPI backend and React web app — including RAG-powered Q&A over filing text.

**Live app:** [signal.harthik.dev](https://signal.harthik.dev)

---

## What Signal Does

| Capability | Description |
|------------|-------------|
| **Explore** | Search any company in the universe, view financial metrics, price indicators, and TradingView charts |
| **Compare** | Side-by-side peer analysis with AI-generated narrative summaries |
| **Knowledge** | Ask natural-language questions about SEC filings; answers are grounded in retrieved filing chunks with compliance guardrails |
| **Signals** | Rule-based master signals (e.g. `STRONG_BUY_OPPORTUNITY`, `QUALITY_MOMENTUM`, `RISK_EXIT`) derived from RSI, revenue growth, margins, and moving averages |

Data coverage spans roughly **May 2021 → present**, sourced from SEC EDGAR (XBRL + filing text) and Polygon.io (daily prices, earnings).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         signal.harthik.dev (Vercel)                     │
│                    React + Vite + Tailwind frontend                     │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ REST /api/*
┌─────────────────────────────────▼───────────────────────────────────────┐
│                    FastAPI backend (Cloud Run / Docker)                 │
│   /company  /prices  /sectors  /compare  /chat/query                    │
│   RAG pipeline · guardrails · rate limiting · optional API key          │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────┐
│              PostgreSQL 15 + pgvector (GCP Cloud SQL / Docker)          │
│   companies · financials · prices · embeddings · query_logs             │
└─────────────────────────────────▲───────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
┌───────▼────────┐     ┌──────────▼──────────┐   ┌────────▼────────┐
│  Apache Airflow│     │   dbt transforms    │   │  ingestion/     │
│  DAGs (Docker) │────▶│  staging → marts    │◀──│  Python library │
│  initial load  │     │  fct_master_signals │   │  EDGAR·Polygon  │
│  daily 8-K     │     │                     │   │  embeddings     │
│  weekly refresh│     │                     │   │                 │
└────────────────┘     └─────────────────────┘   └─────────────────┘
```

---

## Repository Structure

This monorepo contains the full Signal stack. Each top-level directory is a distinct project within the platform:

| Directory | Role |
|-----------|------|
| [`ingestion/`](ingestion/) | Core data pipeline — SEC EDGAR client, Polygon client, XBRL parsing, embedding engine, DB loaders, indicator engine, validation |
| [`airflow/`](airflow/) | Orchestration DAGs: one-time historical load, daily 8-K monitoring, weekly metrics refresh + dbt |
| [`dbt/`](dbt/) | Analytics layer — staging models, YoY growth / price indicators, marts including `fct_master_signals` |
| [`backend/`](backend/) | FastAPI REST API — company profiles, price snapshots, sector counts, peer comparison, RAG chat |
| [`frontend/`](frontend/) | React SPA — Explore, Compare, and Knowledge tabs (desktop-first, 1024px+) |
| [`data_verification/`](data_verification/) | Standalone scripts to verify financials, prices, indicators, embeddings, RAG, and logo URLs |

---

## Company Universe

70 tickers across eight sectors, defined in [`ingestion/config.py`](ingestion/config.py):

- AI & Semiconductors (NVDA, AMD, INTC, …)
- Cloud & Infrastructure (AMZN, MSFT, GOOGL, …)
- Cybersecurity (CRWD, PANW, FTNT, …)
- EV & Energy (TSLA, GM, NEE, …)
- FinTech (V, MA, PYPL, …)
- Biotech & Genomics (MRNA, VRTX, REGN, …)
- Space & Defense (LMT, RTX, RKLB, …)
- Consumer & Retail (WMT, COST, HD, …)

---

## Master Signals

The dbt mart [`fct_master_signals`](dbt/models/marts/fct_master_signals.sql) applies rule-based labels from the latest annual metrics and price indicators:

| Signal | Conditions |
|--------|------------|
| `STRONG_BUY_OPPORTUNITY` | RSI &lt; 30 and revenue growth &gt; 20% |
| `QUALITY_MOMENTUM` | SMA 50 &gt; SMA 200 and net margin &gt; 20% |
| `RISK_EXIT` | RSI &gt; 70 and revenue growth &lt; 0% |
| `MONITOR` | Everything else |

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand, Framer Motion |
| Backend | FastAPI, Pydantic, SQLAlchemy, SlowAPI, LangChain, OpenAI, Voyage AI |
| Data store | PostgreSQL 15, pgvector, Redis |
| Orchestration | Apache Airflow (LocalExecutor) |
| Transform | dbt |
| Ingestion | Python — SEC EDGAR, Polygon.io, pandas, Voyage/OpenAI embeddings |
| Infra | Docker Compose (local), GCP Cloud SQL + Cloud Run (production), Vercel (frontend) |

---

## Local Development

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (frontend)
- Python 3.10+ (optional, for running scripts outside Docker)
- API keys — see [`.env.example`](.env.example)

### 1. Configure environment

```bash
cp .env.example .env
# Fill in: OPENAI_API_KEY, VOYAGE_API_KEY, POLYGON_API_KEY_1/2,
#          DB_PASSWORD, SIGNAL_API_KEY, LOGO_DEV_TOKEN, EDGAR_USER_AGENT_EMAIL
```

### 2. Start the data stack + API

```bash
docker compose up -d
```

This starts:

| Service | URL / Port |
|---------|------------|
| PostgreSQL (pgvector) | `localhost:5433` |
| Redis | `localhost:6379` |
| Airflow UI | [http://localhost:8080](http://localhost:8080) (admin / admin) |
| FastAPI backend | [http://localhost:8000](http://localhost:8000) |

> **Note:** Ollama is intentionally **not** containerized on macOS — run `ollama serve` natively to use the Apple Silicon GPU.

### 3. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Set `VITE_API_URL=http://localhost:8000` and `VITE_SIGNAL_KEY` to match `SIGNAL_API_KEY` in `.env`.

### 4. Trigger data pipelines

In the Airflow UI, unpause and trigger:

- `initial_load` — one-time historical ingest (financials, prices, filings, embeddings)
- `daily_8k_monitor` — daily 8-K detection and embedding refresh
- `weekly_metrics_refresh` — weekly XBRL + price refresh and dbt run

---

## API Overview

Base URL: `http://localhost:8000` (local) or your Cloud Run endpoint (production).

When `SIGNAL_API_KEY` is set, pass it as the `X-Signal-Key` header on all `/api/*` routes.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Service health check |
| `/api/company/{ticker}` | GET | Company profile, metrics, indicators |
| `/api/prices/snapshot` | GET | Price snapshots with logo URLs |
| `/api/sectors/` | GET | Sector breakdown |
| `/api/compare/` | POST | Multi-ticker comparison table |
| `/api/compare/analysis` | POST | AI-generated comparison narrative |
| `/api/chat/query` | POST | RAG Q&A over SEC filings |

---

## Data Verification

Scripts in [`data_verification/`](data_verification/) validate pipeline outputs:

```bash
python data_verification/verify_financials.py
python data_verification/verify_prices.py
python data_verification/verify_indicators.py
python data_verification/verify_embeddings.py
python data_verification/verify_rag.py
python data_verification/verify_logos.py
```

---

## Deployment

| Component | Target |
|-----------|--------|
| Frontend | Vercel (`frontend/vercel.json`) |
| Backend | GCP Cloud Run |
| Database | GCP Cloud SQL (PostgreSQL + pgvector) |
| Orchestration | Airflow on GCP or Docker |

Production CORS allows `https://signal.harthik.dev`. LangSmith tracing is optional — configure `LANGCHAIN_*` variables in `.env`.

---

## Plan Amendments

Approved architecture and implementation changes are logged in [`PLAN_AMENDMENTS.md`](PLAN_AMENDMENTS.md).

---

## License

Private research / portfolio project by [harthikrm](https://github.com/harthikrm). No license file is included yet — contact the maintainer before reuse.

---

## Contributing

This repository is maintained as a personal project. Issues and discussions are welcome; please open a GitHub issue before submitting large changes.
