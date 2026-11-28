CREATE SCHEMA IF NOT EXISTS source_incremental;

COMMENT ON SCHEMA source_incremental IS
    'Synthetic retail source for incremental ingestion tests (updated_at + soft deletes).';
