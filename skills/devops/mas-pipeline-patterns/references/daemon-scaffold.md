# Daemon Scaffold Reference

## Directory Layout

```
supabase/migrations/001_hermes_pipeline.sql
daemon/
  .env.example
  .env
  requirements.txt
  hermes_worker.py
  test_injector.py
  venv/
```

## Setup Commands

```bash
# 1. Create directories
mkdir -p supabase/migrations daemon

# 2. Create venv (requires python3-venv: sudo apt install python3.10-venv)
cd daemon
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Populate .env from .env.example
cp .env.example .env
# Edit .env with real keys

# 4. Run smoke test injection
python test_injector.py

# 5. Start daemon
python hermes_worker.py
```

## .env required keys

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
OPENROUTER_API_KEY=sk-or-v1-your-key
```

## Canonical schema columns (hermes_pipeline)

| Column | Type | Notes |
|--------|------|-------|
| project_id | UUID | PK, auto |
| client_name | VARCHAR(255) | NOT NULL |
| target_domain | VARCHAR(255) | UNIQUE, NOT NULL |
| current_state | hermes_state | ENUM default QUEUED |
| locked_at | TIMESTAMPTZ | Concurrency lock |
| processing_node_id | UUID | Worker that checked out |
| extracted_hex_colors | TEXT[] | From regex on HTML |
| asset_integrity_status | BOOLEAN | Magic number pass |
| gmb_rating | NUMERIC(2,1) | 0.0-5.0 |
| review_count | INTEGER | From GBP |
| simulated_roi_percentage | NUMERIC(6,2) | JCE projection |
| created_at | TIMESTAMPTZ | Auto |
| updated_at | TIMESTAMPTZ | Auto |
| error_log | TEXT | On FAIL |

## State flow

QUEUED -> EXTRACTING -> AUDITING -> VALIDATING -> LIVE
                                  |
                                  v
                                FAILED
```

## Quality gates summary

| # | Gate | Location | What it checks |
|---|------|----------|----------------|
| 1 | Latency | daemon TTFB | < 1500ms (ZA 3G proxy) |
| 2 | Asset MIME | daemon | PNG/JPEG magic bytes, HTTP 200 |
| 3 | GBP Suppression | daemon | gmb_rating >= 4.9 (else MAP_PACK_PENALTY) |
| 4 | Syntax Balance | daemon | balanced brackets in target HTML |
| 5 | Memory Ledger | daemon | MEMORY_<uuid>.md exists on disk |
