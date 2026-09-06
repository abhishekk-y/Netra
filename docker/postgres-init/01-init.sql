CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS events (
    time TIMESTAMPTZ NOT NULL,
    sensor_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    source_ip INET,
    dest_ip INET,
    source_port INT,
    dest_port INT,
    protocol VARCHAR(20),
    community_id VARCHAR(100),
    payload JSONB
);

SELECT create_hypertable('events', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_events_sensor_id ON events (sensor_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_events_ips ON events (source_ip, dest_ip, time DESC);
CREATE INDEX IF NOT EXISTS idx_events_community_id ON events (community_id);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Default admin user (password: admin_change_me)
INSERT INTO users (username, password_hash, role)
VALUES ('admin', crypt('admin_change_me', gen_salt('bf')), 'admin')
ON CONFLICT (username) DO NOTHING;

CREATE TABLE IF NOT EXISTS settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO settings (key, value)
VALUES 
('feature_ml_forecasting', 'true'),
('feature_packet_capture', 'true'),
('performance_profile', '"STANDARD"')
ON CONFLICT (key) DO NOTHING;

CREATE TABLE IF NOT EXISTS mitre_techniques (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tactic VARCHAR(100)
);

INSERT INTO mitre_techniques (id, name, tactic) VALUES
('T1595', 'Active Scanning', 'Reconnaissance'),
('T1110', 'Brute Force', 'Credential Access'),
('T1021', 'Remote Services', 'Lateral Movement'),
('T1071', 'Application Layer Protocol', 'Command and Control'),
('T1041', 'Exfiltration Over C2 Channel', 'Exfiltration')
ON CONFLICT (id) DO NOTHING;
