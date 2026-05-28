# Urban Data Ingestion Platform

A lightweight, config-driven data ingestion system that collects real-time urban and environmental data from multiple APIs and loads it into one or more databases. It supports scheduled pipelines with Apache Airflow, multi-destination writes, email notifications, and observability via OpenTelemetry + Grafana.

---

## What It Does

Each pipeline fetches data from an external API, normalises and transforms it, and writes it to one or more destinations. A post-run email report is sent on success or failure.

**Current pipelines:**

| Pipeline                         | Source                     | Schedule      | Description                                                                 |
| -------------------------------- | -------------------------- | ------------- | --------------------------------------------------------------------------- |
| `ipma_ingestion`                 | IPMA (Portugal Met Office) | Every 3 hours | Weather station observations (temp, wind, humidity, pressure, radiation)    |
| `open_meteo_ingestion`           | Open-Meteo                 | Every 15 min  | Current weather forecast (temp, wind speed/direction)                       |
| `openweathermap_ingestion`       | OpenWeatherMap             | Every 15 min  | Current weather (temp, wind, humidity, pressure, visibility, precipitation) |
| `traffic_flow_ingestion`         | TomTom                     | Every 15 min  | Traffic flow segment data (current speed, free-flow speed, travel times)    |
| `postos_abastecimento_ingestion` | DGEG (Portugal)            | Monthly       | Fuel station locations in the municipality of Maia, Portugal                |

**Supported destinations:**

- **CrateDB** — time-series-optimised distributed SQL
- **MySQL-compatible** — Aiven MySQL, TiDB Cloud (with TLS support)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Apache Airflow                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │ ipma DAG │  │open-meteo│  │  owm DAG │  │  ...   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘  │
└───────┼─────────────┼─────────────┼─────────────┼───────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌───────────────────────────────────────────────────────┐
│                  ingestion/pipelines/                  │
│   fetch → transform → run_inserts → send_email   │
└───────────────────────┬───────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      CrateDB      Aiven MySQL    TiDB Cloud

┌──────────────────────────────────────┐
│  OpenTelemetry Collector             │
│  logs → Grafana Loki                 │
│  host metrics → Grafana Prometheus   │
└──────────────────────────────────────┘
```

---

## Project Structure

```
.
├── dags/                        # Airflow DAG definitions
├── ingestion/
│   ├── pipelines/               # One file per pipeline (run() entrypoint)
│   ├── sources/api.py           # Generic HTTP API client
│   ├── transformations/
│   │   ├── common.py            # Unit conversions (m/s → km/h, wind direction)
│   │   └── time.py              # Timestamp normalization to UTC
│   └── connectors/sql.py        # SQLAlchemy connector (PostgreSQL + MySQL)
├── pipelines_config/              # YAML config files (one per pipeline)
├── utils/
│   ├── common.py                # Environment detection, env secret resolution
│   ├── connectors.py            # Destination dispatch
│   ├── logger.py                # Logging + optional OTLP export
│   └── mailer.py                # Email via Resend or SMTP
├── otel/
│   └── otel-collector-config.yaml
├── config/
│   └── airflow_local_settings.py
├── scripts/
│   └── run_pipeline.py          # Run any pipeline locally without Airflow
├── Dockerfile
├── docker-compose.yaml
└── requirements.txt
```

---

## Running Locally

### Prerequisites

- Docker and Docker Compose
- A `.env` file (see below)

### 1. Create your `.env` file

```env
# Airflow
AIRFLOW_UID=5000
FERNET_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
AIRFLOW__API_AUTH__JWT_SECRET=your_jwt_secret

# API keys
TOM_TOM_API_KEY=...
OPENWEATHERMAP_API_KEY=...

# Destinations
CRATEDB_PASSWORD=...
AIVEN_PASSWORD=...
TIDB_PASSWORD=...

# Email
EMAIL_PASSWORD=...          # Gmail app password (local SMTP)
RESEND_API_KEY=...          # Resend API key (hosted)

# Observability (optional)
LOKI_AUTH=...
GRAFANA_METRICS_AUTH=...
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
```

### 2. Clone and configure

```bash
git clone <repo-url> && cd <repo>
cp .env.example .env  # fill in your secrets
```

### 3. Set up Python environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_pipeline.py pipelines_config/open_meteo.yaml
```

### 4. Start Airflow

```bash
# First time only — initialises the database and creates the admin user
docker compose up airflow-init

# Build the image
docker compose build

# Start all services in detached mode
docker compose up -d
```

Airflow UI will be available at **http://localhost:8081** (default credentials: `airflow` / `airflow`).

DAGs are paused by default — unpause the ones you want to run from the UI.

### 5. Shut down

```bash
docker compose down
```

To also remove the database volume (full reset):

```bash
docker compose down -v
```

## Adding a New Pipeline

**1. Create a config file** `pipelines_config/my_pipeline.yaml`:

```yaml
pipeline_name: my_pipeline_ingestion
source:
  name: MySource
  type: api
  base_url: https://api.example.com
  endpoint: /data
  parameters:
    api_key: $MY_API_KEY
destinations:
  - type: crate
    name: CrateDB
    host: ...
    table: my_table
    username: admin
    password: $CRATEDB_PASSWORD
email:
  send: true
  from: you@example.com
  api_key: $RESEND_API_KEY
  subject: My Pipeline Report
  recipients:
    - you@example.com
```

**2. Create a pipeline module** `ingestion/pipelines/my_pipeline.py` following the pattern in any existing pipeline: fetch → transform → `run_inserts(config, data)` → email in `finally`.

**3. Create a DAG** `dags/my_pipeline_dag.py` following any existing DAG.

**4. Register in `scripts/run_pipeline.py`** if you want local execution support.

## Observability

Logs are exported via OpenTelemetry to **Grafana Loki**. Host metrics (CPU, memory, disk, network) are scraped and pushed to **Grafana Prometheus**. Both are configured in `otel/otel-collector-config.yaml`.

If `OTEL_EXPORTER_OTLP_ENDPOINT` is not set, logging falls back to stdout only.
