CREATE TABLE "qr" (
    id SERIAL PRIMARY KEY,
    unique_hex VARCHAR(20) NOT NULL UNIQUE,
    kit_id INT NOT NULL,
    FOREIGN KEY (kit_id) REFERENCES "kit"(id),
    is_used BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX ON "qr" (unique_hex);
CREATE INDEX ON "qr" (kit_id);
ANALYZE "qr";