CREATE TABLE user_statuses (
    id SERIAL PRIMARY KEY,
    details status_info
);
INSERT INTO user_statuses (details)
VALUES
    (ROW('admin', 'User has administrative privileges', 0)),
    (ROW('volunteer', 'User has contributed to researches', 0)),
    (ROW('observer', 'Default status for new users', 0));

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    status INT NOT NULL DEFAULT 3,
    FOREIGN KEY (status) REFERENCES user_statuses(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    password_hash VARCHAR(128) NOT NULL,
    password_salt VARCHAR(32) NOT NULL,
    n_samples_collected INT NOT NULL DEFAULT 0
);
-- Autoupdating `updated_at`
CREATE TRIGGER autoupdate_user
BEFORE INSERT OR UPDATE ON "user"
FOR EACH ROW
EXECUTE FUNCTION refresh_last_updated();

CREATE TRIGGER user_status_trigger
BEFORE INSERT OR UPDATE ON "user"
FOR EACH ROW
EXECUTE FUNCTION update_status_n('user_statuses');


CREATE INDEX ON "user" (name);
CREATE INDEX ON "user" (status);
ANALYZE "user";


