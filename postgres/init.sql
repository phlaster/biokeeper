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
    ('admin', 'User has administrative privileges'),
    ('volunteer', 'User has contributed to researches'),
    ('observer', 'Default status for new users');
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    user_status INT NOT NULL DEFAULT 3,
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
CREATE INDEX ON users (username);
CREATE INDEX ON users (user_status);
CREATE INDEX ON user_statuses (status_id);
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
    research_name TEXT NOT NULL,
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
CREATE INDEX ON researches (research_status);
CREATE INDEX ON researches (research_name);
CREATE INDEX ON researches (created_by);
CREATE INDEX ON researches (day_start);
CREATE INDEX ON researches (day_end);
CREATE INDEX ON research_statuses (status_key);
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
    kit_unique_code BYTEA NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    kit_status INT NOT NULL DEFAULT 1,
    FOREIGN KEY (kit_status) REFERENCES kit_statuses(status_id),
    n_qrs INT NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TRIGGER autoupdate_kits
BEFORE INSERT OR UPDATE ON kits
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();
CREATE INDEX ON kits (user_id);
CREATE INDEX ON kits (user_id);
CREATE INDEX ON kits (kit_unique_code);
CREATE INDEX ON kit_statuses (status_key);
--------------------------------------------------------------------



CREATE TABLE qrs (
    qr_id SERIAL PRIMARY KEY,
    qr_unique_code BYTEA NOT NULL,
    kit_id INT NOT NULL,
    FOREIGN KEY (kit_id) REFERENCES kits(kit_id),
    is_used BOOLEAN DEFAULT false
);
CREATE INDEX ON qrs (is_used);
CREATE INDEX ON qrs (qr_unique_code);


CREATE TABLE samples (
    sample_id SERIAL PRIMARY KEY,
    research_id INT NOT NULL,
    FOREIGN KEY (research_id) REFERENCES researches(research_id),
    qr_id INT NOT NULL,
    FOREIGN KEY (qr_id) REFERENCES qrs(qr_id),
    collected_at TIMESTAMP NOT NULL,
    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    in_lab_at TIMESTAMP,
    gps POINT,
    weather_conditions TEXT,
    user_comment TEXT,
    photo BYTEA -- https://www.postgresql.org/docs/7.4/jdbc-binary-data.html
);
CREATE INDEX ON samples (research_id);
CREATE INDEX ON samples (collected_at);
CREATE INDEX ON samples (qr_id);



------------------------ INDEXING ---------------------------------------
ANALYZE user_statuses;
ANALYZE users;
ANALYZE research_statuses;
ANALYZE researches;
ANALYZE kit_statuses;
ANALYZE kits;
ANALYZE qrs;
ANALYZE samples;