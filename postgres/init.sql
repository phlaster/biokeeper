CREATE TABLE researches (
    research_id SERIAL PRIMARY KEY,
    research_type INT NOT NULL,
    num_samp INT NOT NULL,
    day_start DATE NOT NULL,
    day_end DATE
);

CREATE TABLE generated_qrs (
    qr_id SERIAL PRIMARY KEY,
    research_id INT NOT NULL,
    qr_text TEXT NOT NULL,
    FOREIGN KEY (research_id) REFERENCES researches(research_id)
);

CREATE TABLE collected_samples (
    id_sample SERIAL PRIMARY KEY,
    qr_id INT NOT NULL,
    date DATE NOT NULL,
    time TIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    temperature INT,
    gps POINT,
    FOREIGN KEY (qr_id) REFERENCES generated_qrs(qr_id)
);

CREATE TABLE global_counters (
    counter_qr INT NOT NULL,
    counter_research INT NOT NULL
);

-- Initialize the global counters
INSERT INTO global_counters (counter_qr, counter_research) VALUES (0, 0);