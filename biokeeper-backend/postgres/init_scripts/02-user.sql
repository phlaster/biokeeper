CREATE TABLE "user" (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    n_samples_collected INT NOT NULL DEFAULT 0
);
-- Autoupdating `updated_at`
CREATE TRIGGER autoupdate_user
BEFORE INSERT OR UPDATE ON "user"
FOR EACH ROW
EXECUTE FUNCTION refresh_last_updated();


CREATE INDEX ON "user" (name);
ANALYZE "user";


