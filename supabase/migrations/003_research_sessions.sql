-- 003_research_sessions.sql
-- Track each end-to-end research cycle for the Triple Output Pipeline
-- Part of Phase 0.5b: Research Engine MVP

CREATE TABLE IF NOT EXISTS research_sessions (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

  -- What was researched
  ticker TEXT NOT NULL,
  session_type TEXT NOT NULL,      -- 'full_analysis' | 'update' | 'event_response'
  trigger_source TEXT NOT NULL,    -- 'inbox_task' | 'scheduled' | 'manual' | 'event'

  -- Who ran it
  initiated_by TEXT NOT NULL,      -- 'allen' | 'jane' | 'jack' | 'detective' | 'skeptic'
  executed_by TEXT,                -- actual executor (e.g. 'jack' when jane dispatches)

  -- Parameters used (frozen at execution time)
  parameters JSONB NOT NULL,

  -- Triple Output tracking
  output_obsidian TEXT,            -- path: 'research/companies/klac/2026-02-17.md'
  output_supabase_iv_id BIGINT,   -- FK -> iv_calculations.id
  output_blog_draft TEXT,          -- path: 'docs/blog/draft-klac-analysis.md'

  -- Status
  status TEXT DEFAULT 'running',   -- 'running' | 'completed' | 'failed' | 'review'
  error_message TEXT,

  -- Timing
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,

  -- Metadata
  notes TEXT,
  inbox_task_ref TEXT              -- inbox file path that triggered this
);

-- Index for dashboard queries
CREATE INDEX IF NOT EXISTS idx_rs_ticker_date
  ON research_sessions (ticker, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_rs_status
  ON research_sessions (status) WHERE status != 'completed';
