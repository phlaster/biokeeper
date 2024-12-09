CREATE TABLE research_statuses (
    id SERIAL PRIMARY KEY,
    details status_info
);
INSERT INTO research_statuses (details)
VALUES
    (ROW('pending', 'The research has been created, but has not started yet', 0)),
    (ROW('ongoing', 'The research is on', 0)),
    (ROW('paused', 'The research has been paused', 0)),
    (ROW('ended', 'The research has ended', 0)),
    (ROW('canceled', 'The research has been canceled', 0));

CREATE TABLE "research" (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    status INT NOT NULL DEFAULT 1,
    FOREIGN KEY (status) REFERENCES research_statuses(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL,
    FOREIGN KEY (created_by) REFERENCES "user"(id),
    day_start DATE NOT NULL,
    day_end DATE,
    n_samples INT NOT NULL DEFAULT 0,
    comment TEXT,
    approval_required BOOLEAN NOT NULL DEFAULT TRUE
);
-- Autoupdating `updated_at`
CREATE TRIGGER autoupdate_researches
BEFORE INSERT OR UPDATE ON "research"
FOR EACH ROW
EXECUTE FUNCTION refresh_last_updated();

CREATE TRIGGER research_status_trigger
BEFORE INSERT OR UPDATE ON "research"
FOR EACH ROW    
EXECUTE FUNCTION update_status_n('research_statuses');

CREATE INDEX ON "research" (name);
CREATE INDEX ON "research" (status);
CREATE INDEX ON "research" (created_by);
ANALYZE "research";
