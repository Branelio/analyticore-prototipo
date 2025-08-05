CREATE TABLE IF NOT EXISTS jobs (
    job_id UUID PRIMARY KEY,
    text_to_analyze TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    sentiment VARCHAR(10),
    keywords TEXT[],
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);