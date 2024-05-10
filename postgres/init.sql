-- Function to update timestamp in `updated_at` as the table modifies
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;







-------------------------- USERS ------------------------
CREATE TABLE user_statuses (
    status_id SERIAL PRIMARY KEY,
    status_key TEXT NOT NULL,
    status_info TEXT DEFAULT ''
);
INSERT INTO user_statuses (status_key, status_info)
VALUES 
    ('observer', 'Default status for new users'),
    ('volunteer', 'User has contributed to researches'),
    ('admin', 'User has administrative privileges');
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    user_status INT NOT NULL DEFAULT 1,
    FOREIGN KEY (user_status) REFERENCES user_statuses(status_id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    password_hash BYTEA NOT NULL,
    password_salt BYTEA NOT NULL,
    n_samples_collected INT NOT NULL DEFAULT 0
);
CREATE TRIGGER autoupdate_users
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();
-----------------------------------------------------











---------------------- RESEARCHES ------------------------
CREATE TABLE research_statuses (
    status_id SERIAL PRIMARY KEY,
    status_key TEXT NOT NULL,
    status_info TEXT DEFAULT ''
);
INSERT INTO research_statuses (status_key, status_info)
VALUES 
    ('pending', 'The research has been created, but has not started yet'),
    ('ongoing', 'The research is on'),
    ('paused', 'The research has been paused'),
    ('ended', 'The research has ended'),
    ('cancelled', 'The research has been cancelled');
CREATE TABLE researches (
    research_id SERIAL PRIMARY KEY,
    research_type TEXT NOT NULL,
    research_status INT NOT NULL DEFAULT 1,
    FOREIGN KEY (research_status) REFERENCES research_statuses(status_id),
    research_comment TEXT DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    day_start DATE NOT NULL,
    day_end DATE,
    n_samples INT NOT NULL DEFAULT 0
);
CREATE TRIGGER autoupdate_researches
BEFORE INSERT OR UPDATE ON researches
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();
----------------------------------------------------








-------------------------- KITS ------------------------------------
CREATE TABLE kit_statuses (
    status_id SERIAL PRIMARY KEY,
    status_key TEXT NOT NULL,
    status_info TEXT DEFAULT ''
);
INSERT INTO kit_statuses (status_key, status_info)
VALUES 
    ('created', 'The kit was created'),
    ('sent', 'The kit was sent'),
    ('activated', 'The kit was recieved by a volunteer');
CREATE TABLE kits (
    kit_id SERIAL PRIMARY KEY,
    kit_unique_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    kit_status INT NOT NULL DEFAULT 1,
    FOREIGN KEY (kit_status) REFERENCES kit_statuses(status_id),
    n_qrs INT NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
--------------------------------------------------------------------













CREATE TABLE qrs (
    qr_id SERIAL PRIMARY KEY,
    qr_unique_code TEXT NOT NULL,
    kit_id INT NOT NULL,
    FOREIGN KEY (kit_id) REFERENCES kits(kit_id),
    is_used BOOLEAN DEFAULT false
);

CREATE TABLE samples (
    sample_id SERIAL PRIMARY KEY,
    research_id INT NOT NULL,
    FOREIGN KEY (research_id) REFERENCES researches(research_id),
    qr_id INT NOT NULL,
    FOREIGN KEY (qr_id) REFERENCES qrs(qr_id),
    collected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gps POINT,
    weather_conditions TEXT,
    user_comment TEXT,
    photo BYTEA -- https://www.postgresql.org/docs/7.4/jdbc-binary-data.html
);








------------------------ INDEXING ---------------------------------------
CREATE INDEX idx_username ON users (username);
CREATE INDEX idx_user_status ON users (user_status);
CREATE INDEX idx_research_status ON researches (research_status);
CREATE INDEX idx_created_by ON researches (created_by);
CREATE INDEX idx_day_start ON researches (day_start);
CREATE INDEX idx_day_end ON researches (day_end);
CREATE INDEX idx_user_id ON kits (user_id);
CREATE INDEX idx_kit_status ON kits (kit_status);
CREATE INDEX idx_is_used ON qrs (is_used);
CREATE INDEX idx_research_id ON samples (research_id);
CREATE INDEX idx_collected_at ON samples (collected_at);
