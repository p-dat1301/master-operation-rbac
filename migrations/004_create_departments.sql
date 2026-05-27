CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    level SMALLINT NOT NULL,
    parent_id INTEGER NULL,
    head_id INTEGER NULL,
    code VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_department_level CHECK (level IN (1, 2, 3, 4)),
    CONSTRAINT fk_department_parent
        FOREIGN KEY (parent_id) REFERENCES departments (id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_departments_code ON departments(code);

CREATE INDEX IF NOT EXISTS idx_departments_parent ON departments(parent_id);

CREATE INDEX IF NOT EXISTS idx_departments_head ON departments(head_id);