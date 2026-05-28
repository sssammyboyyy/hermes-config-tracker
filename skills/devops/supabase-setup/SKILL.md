---
name: supabase-setup
description: "Supabase project setup, migration patterns, RLS handling, and daemon integration. Covers the full lifecycle from schema design to live pipeline."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [supabase, database, migrations, rls, daemon, pipeline]
    related_skills: [mas-pipeline-patterns, hermes-config]
---

# Supabase Setup

Complete guide for Supabase projects in the MAS ecosystem. Covers schema design, migration patterns, RLS handling, and Python daemon integration.

## Critical Rules

### 1. RLS Is Enabled by Default
Every new table in Supabase has Row Level Security (RLS) enabled by default. The anon key is **denied** unless you explicitly disable RLS or add a permissive policy.

**Always include in migration SQL:**
```sql
ALTER TABLE your_table DISABLE ROW LEVEL SECURITY;
```

Or with a policy:
```sql
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON your_table FOR ALL USING (true);
```

**Verification after migration:**
```python
supabase.table('your_table').insert({"test": "value"}).execute()
# If 42501 error → RLS still blocking
```

### 2. Migration File Naming
Use sequential numeric prefixes: `001_hermes_pipeline.sql`, `002_add_indexes.sql`, etc.
Store in `/home/samuelj121314/supabase/migrations/`.

### 3. ENUM Types for State Machines
Use PostgreSQL ENUM types for pipeline states — they're faster than VARCHAR and self-documenting:
```sql
CREATE TYPE hermes_state AS ENUM ('QUEUED', 'EXTRACTING', 'AUDITING', 'VALIDATING', 'LIVE', 'FAILED');
```

### 4. Atomic RPC for Queue Checkout
Use `FOR UPDATE SKIP LOCKED` in RPC functions for concurrent-safe job checkout:
```sql
CREATE OR REPLACE FUNCTION checkout_hermes_task(worker_id UUID)
RETURNS SETOF hermes_pipeline AS $$
BEGIN
  RETURN QUERY
  UPDATE hermes_pipeline
  SET locked_at = NOW(), processing_node_id = worker_id, current_state = 'EXTRACTING'
  WHERE project_id = (
    SELECT project_id FROM hermes_pipeline
    WHERE current_state = 'QUEUED' AND locked_at IS NULL
    FOR UPDATE SKIP LOCKED LIMIT 1
  )
  RETURNING *;
END;
$$ LANGUAGE plpgsql;
```

### 5. Selective Indexes for Queue Workers
Index only the rows the daemon actually queries:
```sql
CREATE INDEX idx_hermes_queue ON hermes_pipeline (current_state)
WHERE current_state = 'QUEUED' AND locked_at IS NULL;
```

## Schema: hermes_pipeline

See `references/schema-hermes-pipeline.sql` for the full canonical schema.

Key columns:
- `project_id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
- `client_name VARCHAR(255) NOT NULL`
- `target_domain VARCHAR(255) UNIQUE NOT NULL`
- `current_state hermes_state DEFAULT 'QUEUED'`
- `locked_at TIMESTAMPTZ` — concurrency lock
- `processing_node_id UUID` — which daemon node has the job
- `extracted_hex_colors TEXT[]` — brand colors from target site
- `asset_integrity_status BOOLEAN` — Gate 2 result
- `gmb_rating NUMERIC(2,1)` — Google Business Profile rating
- `review_count INTEGER`
- `simulated_roi_percentage NUMERIC(6,2)`
- `error_log TEXT` — failure reason if state = 'FAILED'

## Python Daemon Integration

### Environment
The daemon reads from `/home/samuelj121314/daemon/.env`:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
OPENROUTER_API_KEY=sk-or-...
```

### Connection Pattern
```python
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv('/home/samuelj121314/daemon/.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
```

### Insert (Test Injector)
```python
response = supabase.table('hermes_pipeline').insert({
    "client_name": "Client Name",
    "target_domain": "https://client.com",
    "current_state": "QUEUED"
}).execute()
project_id = response.data[0]['project_id']
```

### RPC Checkout (Daemon)
```python
response = supabase.rpc('checkout_hermes_task', {'worker_id': NODE_ID}).execute()
jobs = response.data
if jobs:
    await process_job(jobs[0])
```

### Update State
```python
supabase.table('hermes_pipeline').update({
    'current_state': 'LIVE',
    'extracted_hex_colors': colors,
    'gmb_rating': 4.8
}).eq('project_id', project_id).execute()
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `42501: row-level security` | RLS enabled, no policy | `ALTER TABLE ... DISABLE ROW LEVEL SECURITY;` |
| `PGRST204: column does not exist` | Column name mismatch | Check schema: `gmb_rating` not `rating` |
| `duplicate key value` | target_domain UNIQUE violation | Use `.upsert()` or check before insert |
| `rpc function not found` | Migration not applied | Run SQL in Supabase dashboard |
| `JWT expired` | Anon key expired | Regenerate in Supabase dashboard → Settings → API |

## Version History

v1.0 (2026-05-28): Initial skill. RLS rules, schema, RPC patterns, daemon integration, troubleshooting table.
