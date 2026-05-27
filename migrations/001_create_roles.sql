CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_role_name 
        CHECK (name IN('admin', 'bod', 'manager', 'employee'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_roles_name ON roles(name);