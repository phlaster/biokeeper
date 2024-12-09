CREATE TABLE kit_statuses (
    id SERIAL PRIMARY KEY,
    details status_info
);
INSERT INTO kit_statuses (details)
VALUES
    (ROW('created', 'The kit was created', 0)),
    (ROW('sent', 'The kit was sent', 0)),
    (ROW('activated', 'The kit was recieved by a volunteer', 0));

CREATE TABLE "kit" (
    id SERIAL PRIMARY KEY,
    unique_hex VARCHAR(16) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status INT NOT NULL DEFAULT 1,
    FOREIGN KEY (status) REFERENCES kit_statuses(id),
    n_qrs INT NOT NULL,
    creator_id INT NOT NULL,
    owner_id INT,
    FOREIGN KEY (creator_id) REFERENCES "user"(id),
    FOREIGN KEY (owner_id) REFERENCES "user"(id)
);

CREATE TRIGGER autoupdate_kits
BEFORE INSERT OR UPDATE ON "kit"
FOR EACH ROW
EXECUTE FUNCTION refresh_last_updated();

CREATE TRIGGER kit_status_trigger
BEFORE INSERT OR UPDATE ON "kit"
FOR EACH ROW
EXECUTE FUNCTION update_status_n('kit_statuses');

CREATE INDEX ON "kit" (owner_id);
CREATE INDEX ON "kit" (unique_hex);
ANALYZE "kit";
