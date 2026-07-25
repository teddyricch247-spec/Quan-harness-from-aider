-- إعدادات الأداء والمفاتيح الأجنبية
-- سيتم تفعيلها من database.py:
-- PRAGMA foreign_keys = ON;
-- PRAGMA journal_mode = WAL;
-- PRAGMA synchronous = NORMAL;

-- تتبع إصدار المخطط
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- إعدادات النظام
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'string',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- المستودعات
CREATE TABLE IF NOT EXISTS repositories (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    default_branch TEXT NOT NULL DEFAULT 'main',
    current_branch TEXT,
    local_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    last_pull_at TIMESTAMP,
    last_commit TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- المهام
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    repository_id TEXT NOT NULL,
    message TEXT NOT NULL,
    model TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    pid INTEGER,
    exit_code INTEGER,
    log_path TEXT,
    error_message TEXT,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);

-- سجل أحداث المهام
CREATE TABLE IF NOT EXISTS job_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    event TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- الفهارس لتحسين الأداء
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_repository ON jobs(repository_id);
CREATE INDEX IF NOT EXISTS idx_job_events_job ON job_events(job_id);
CREATE INDEX IF NOT EXISTS idx_repositories_status ON repositories(status);

-- إدراج الإصدار الأولي
INSERT INTO schema_version (version) VALUES (1);
