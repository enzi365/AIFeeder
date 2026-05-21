-- AIFeeder schema. Single-user local SQLite. Idempotent (IF NOT EXISTS).
-- Future-MVP columns are present from v1 even when unused in the slice.

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL CHECK (source_type IN ('rss', 'youtube_channel')),
    why TEXT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_polled_at TIMESTAMP,
    consecutive_failures INTEGER DEFAULT 0,
    last_error_at TIMESTAMP,
    last_error_message TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    external_id TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    raw_content TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processed', 'skipped', 'failed')),
    failure_class TEXT
        CHECK (failure_class IS NULL OR failure_class IN ('transient', 'permanent', 'content', 'unknown')),
    failure_message TEXT,
    is_read INTEGER NOT NULL DEFAULT 0,
    UNIQUE (source_id, external_id)
);

CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
CREATE INDEX IF NOT EXISTS idx_items_fetched_at ON items(fetched_at DESC);

CREATE TABLE IF NOT EXISTS summaries (
    item_id INTEGER PRIMARY KEY REFERENCES items(id),
    relevance_verdict TEXT NOT NULL
        CHECK (relevance_verdict IN ('yes', 'no', 'maybe')),
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    relevance_reason TEXT,
    content_type_tag TEXT,
    key_points_json TEXT,
    chapter_index_json TEXT,
    model_used TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id),
    thumb TEXT NOT NULL CHECK (thumb IN ('up', 'down')),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cost_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER REFERENCES items(id),
    model TEXT NOT NULL,
    tokens_in INTEGER NOT NULL,
    tokens_out INTEGER NOT NULL,
    cost_usd REAL NOT NULL,
    operation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed: v1 sources. INSERT OR IGNORE = idempotent across re-runs.
INSERT OR IGNORE INTO sources (name, url, source_type, why) VALUES
    ('Simon Willison',
     'https://simonwillison.net/atom/everything/',
     'rss',
     'Follow practical AI engineering — new LLM models, working code examples, real engineering insights from someone shipping AI products. Filter out Datasette / Django / general web-dev posts that are not about AI.'),
    ('ArXiv: AI',
     'https://arxiv.org/rss/cs.AI',
     'rss',
     'Stay aware of new research in machine learning and AI agents. Prefer applied / systems-level work over highly mathematical / formal-methods papers I would not engage with as a builder.');
