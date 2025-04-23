-- 02_session.sql

CREATE TABLE session (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id),
    refresh_token_hash VARCHAR(128) NOT NULL,
    device_ip TEXT NOT NULL,
    device_info TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
