CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    employee_code VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(30) NULL,
    job_title VARCHAR(255) NULL,
    contact_type VARCHAR(50) NULL,
    role_id INTEGER NOT NULL,
    department_id INTEGER NULL,
    manager_id INTEGER NULL,
    zalo_id VARCHAR(50),
    telegram_id VARCHAR(50),
    hire_date DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_user_contact_type 
        CHECK (contact_type IN ('probation', 'official', 'service')),
    CONSTRAINT fk_user_role
        FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE RESTRICT,
    CONSTRAINT fk_user_department
        FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE RESTRICT,
    CONSTRAINT fk_user_manager
        FOREIGN KEY (manager_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_employee_code ON users(employee_code);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE INDEX IF NOT EXISTS 