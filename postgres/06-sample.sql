CREATE TABLE sample_statuses (
    id SERIAL PRIMARY KEY,
    details status_info
);
INSERT INTO sample_statuses (details)
VALUES
    (ROW('collected', 'The sample was collected by the volunteer', 0)),
    (ROW('sent', 'The sample was sent to the lab', 0)),
    (ROW('delivered', 'The sample was delivered to the lab', 0));

CREATE TABLE "sample" (
    id SERIAL PRIMARY KEY,
    research_id INT NOT NULL,
    FOREIGN KEY (research_id) REFERENCES "research"(id),
    qr_id INT NOT NULL,
    FOREIGN KEY (qr_id) REFERENCES "qr"(id),
    status INT NOT NULL DEFAULT 1,
    FOREIGN KEY (status) REFERENCES "sample_statuses"(id),
    owner_id INT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES "user"(id),
    collected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_to_lab_at TIMESTAMP WITH TIME ZONE,
    delivered_to_lab_at TIMESTAMP WITH TIME ZONE,
    gps POINT NOT NULL,
    weather JSON,
    comment TEXT,
    photo BYTEA -- https://www.postgresql.org/docs/7.4/jdbc-binary-data.html
);
CREATE TRIGGER autoupdate_sample
BEFORE INSERT OR UPDATE ON "user"
FOR EACH ROW
EXECUTE FUNCTION refresh_last_updated();

CREATE TRIGGER sample_status_trigger
BEFORE INSERT OR UPDATE ON "sample"
FOR EACH ROW
EXECUTE FUNCTION update_status_n('sample_statuses');

CREATE INDEX ON "sample" (research_id);
CREATE INDEX ON "sample" (qr_id);
ANALYZE "sample";
