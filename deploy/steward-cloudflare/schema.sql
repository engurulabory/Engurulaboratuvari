CREATE TABLE IF NOT EXISTS steward_cycles (
  cycle_id TEXT PRIMARY KEY,
  started_at TEXT NOT NULL,
  finished_at TEXT NOT NULL,
  status TEXT NOT NULL,
  repo_count INTEGER NOT NULL,
  inventory_digest TEXT NOT NULL,
  detail_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS steward_inventory (
  repository TEXT PRIMARY KEY,
  first_seen_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  visibility TEXT,
  default_branch TEXT,
  archived INTEGER NOT NULL DEFAULT 0,
  fork INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT,
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS steward_findings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL,
  kind TEXT NOT NULL,
  repository TEXT,
  state TEXT NOT NULL,
  detail_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_steward_cycles_finished ON steward_cycles(finished_at DESC);
CREATE INDEX IF NOT EXISTS idx_steward_findings_at ON steward_findings(at DESC);
