CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    token TEXT NOT NULL,
    title TEXT NOT NULL,
    owner_email TEXT,
    main_site TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_metadata (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    metadata_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS runs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    run_token TEXT NOT NULL,
    status TEXT,
    pages_scraped INTEGER DEFAULT 0,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    records_count INTEGER DEFAULT 0,
    data_file TEXT,
    is_empty BOOLEAN DEFAULT 0,
    is_continuation BOOLEAN DEFAULT 0,
    completion_percentage REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS scraped_data (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    data_key TEXT,
    data_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    date TEXT,
    total_pages INTEGER DEFAULT 0,
    total_records INTEGER DEFAULT 0,
    runs_count INTEGER DEFAULT 0,
    avg_duration REAL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recovery_operations (
    id SERIAL PRIMARY KEY,
    original_run_id INTEGER NOT NULL,
    recovery_run_id INTEGER,
    project_id INTEGER NOT NULL,
    original_project_token TEXT,
    recovery_project_token TEXT,
    last_product_url TEXT,
    last_product_name TEXT,
    stopped_timestamp TIMESTAMP,
    recovery_triggered_timestamp TIMESTAMP,
    recovery_started_timestamp TIMESTAMP,
    recovery_completed_timestamp TIMESTAMP,
    status TEXT DEFAULT 'pending',
    original_data_count INTEGER DEFAULT 0,
    recovery_data_count INTEGER DEFAULT 0,
    final_data_count INTEGER DEFAULT 0,
    duplicates_removed INTEGER DEFAULT 0,
    attempt_number INTEGER DEFAULT 1,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_lineage (
    id SERIAL PRIMARY KEY,
    scraped_data_id INTEGER NOT NULL,
    source_run_id INTEGER NOT NULL,
    recovery_operation_id INTEGER,
    is_duplicate BOOLEAN DEFAULT 0,
    duplicate_of_data_id INTEGER,
    product_url TEXT,
    product_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS run_checkpoints (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL,
    snapshot_timestamp TIMESTAMP,
    item_count_at_time INTEGER,
    items_per_minute REAL,
    estimated_completion_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS monitoring_sessions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    run_token TEXT NOT NULL,
    target_pages INTEGER DEFAULT 1,
    status TEXT DEFAULT 'active',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_records INTEGER DEFAULT 0,
    total_pages INTEGER DEFAULT 0,
    progress_percentage REAL DEFAULT 0,
    current_url TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scraped_records (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    run_token TEXT NOT NULL,
    page_number INTEGER,
    data_hash TEXT,
    data_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics_cache (
    id SERIAL PRIMARY KEY,
    project_token TEXT NOT NULL,
    run_token TEXT,
    total_records INTEGER DEFAULT 0,
    total_fields INTEGER DEFAULT 0,
    total_runs INTEGER DEFAULT 0,
    completed_runs INTEGER DEFAULT 0,
    progress_percentage REAL DEFAULT 0,
    status TEXT,
    analytics_json TEXT,
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS csv_exports (
    id SERIAL PRIMARY KEY,
    project_token TEXT NOT NULL,
    run_token TEXT,
    csv_data TEXT,
    row_count INTEGER DEFAULT 0,
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics_records (
    id SERIAL PRIMARY KEY,
    project_token TEXT NOT NULL,
    run_token TEXT NOT NULL,
    record_index INTEGER,
    record_data TEXT NOT NULL,
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scraping_sessions (
    id SERIAL PRIMARY KEY,
    project_token TEXT NOT NULL,
    project_name TEXT NOT NULL,
    total_pages_target INTEGER NOT NULL,
    current_iteration INTEGER DEFAULT 1,
    pages_completed INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS iteration_runs (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    iteration_number INTEGER NOT NULL,
    parsehub_project_token TEXT NOT NULL,
    parsehub_project_name TEXT NOT NULL,
    start_page_number INTEGER NOT NULL,
    end_page_number INTEGER NOT NULL,
    pages_in_this_run INTEGER NOT NULL,
    run_token TEXT NOT NULL,
    csv_data TEXT,
    records_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS combined_scraped_data (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    consolidated_csv TEXT,
    total_records INTEGER DEFAULT 0,
    total_pages_scraped INTEGER DEFAULT 0,
    deduplicated_record_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS url_patterns (
    id SERIAL PRIMARY KEY,
    project_token TEXT NOT NULL,
    original_url TEXT NOT NULL,
    pattern_type TEXT,
    pattern_regex TEXT,
    last_page_placeholder TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS import_batches (
    id SERIAL PRIMARY KEY,
    file_name TEXT NOT NULL,
    record_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'success',
    error_message TEXT,
    uploaded_by TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metadata (
    id SERIAL PRIMARY KEY,
    personal_project_id TEXT NOT NULL,
    project_id INTEGER,
    project_token TEXT,
    project_name TEXT NOT NULL,
    last_run_date TIMESTAMP,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    region TEXT,
    country TEXT,
    brand TEXT,
    website_url TEXT,
    total_pages INTEGER,
    total_products INTEGER,
    current_page_scraped INTEGER DEFAULT 0,
    current_product_scraped INTEGER DEFAULT 0,
    last_known_url TEXT,
    import_batch_id INTEGER,
    status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS product_data (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    run_id INTEGER,
    run_token TEXT,
    name TEXT,
    part_number TEXT,
    brand TEXT,
    list_price REAL,
    sale_price REAL,
    case_unit_price REAL,
    country TEXT,
    currency TEXT,
    product_url TEXT,
    page_number INTEGER,
    extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metadata_project_token ON metadata(project_token);

CREATE INDEX IF NOT EXISTS idx_runs_project_id ON runs(project_id);