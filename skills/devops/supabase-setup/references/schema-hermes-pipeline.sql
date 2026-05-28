-- Canonical hermes_pipeline schema for MAS daemon
-- Apply via Supabase SQL Editor

CREATE TYPE hermes_state AS ENUM ('QUEUED', 'EXTRACTING', 'AUDITING', 'VALIDATING', 'LIVE', 'FAILED');

CREATE TABLE hermes_pipeline (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_name VARCHAR(255) NOT NULL,
    target_domain VARCHAR(255) UNIQUE NOT NULL,
    current_state hermes_state DEFAULT 'QUEUED',
    locked_at TIMESTAMPTZ,
    processing_node_id UUID,
    extracted_hex_colors TEXT[] DEFAULT '{}',
    asset_integrity_status BOOLEAN DEFAULT FALSE,
    gmb_rating NUMERIC(2,1) CHECK (gmb_rating >= 0.0 AND gmb_rating <= 5.0),
    review_count INTEGER DEFAULT 0,
    simulated_roi_percentage NUMERIC(6,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    error_log TEXT
);

-- CRITICAL: Disable RLS for daemon access via anon key
ALTER TABLE hermes_pipeline DISABLE ROW LEVEL SECURITY;

CREATE INDEX idx_hermes_queue ON hermes_pipeline (current_state)
WHERE current_state = 'QUEUED' AND locked_at IS NULL;

CREATE OR REPLACE FUNCTION checkout_hermes_task(worker_id UUID)
RETURNS SETOF hermes_pipeline AS $$
BEGIN
  RETURN QUERY
  UPDATE hermes_pipeline
  SET locked_at = NOW(),
      processing_node_id = worker_id,
      current_state = 'EXTRACTING',
      updated_at = NOW()
  WHERE project_id = (
    SELECT project_id FROM hermes_pipeline
    WHERE current_state = 'QUEUED' AND locked_at IS NULL
    FOR UPDATE SKIP LOCKED
    LIMIT 1
  )
  RETURNING *;
END;
$$ LANGUAGE plpgsql;
