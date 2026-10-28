CREATE TABLE IF NOT EXISTS sessions (
    session_id     TEXT PRIMARY KEY,
    schema_version TEXT,
    exercise_name  TEXT,
    config_version TEXT,
    started_at     TEXT,
    ended_at       TEXT,
    rep_count      INTEGER,
    attempted_reps INTEGER
);

CREATE TABLE IF NOT EXISTS flags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT,
    rule_id     TEXT,
    timestamp   TEXT,
    reason      TEXT,
    confidence  REAL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);