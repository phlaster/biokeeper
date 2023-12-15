-- Create the reseach Table
CREATE TABLE reseach (
    id_res SERIAL PRIMARY KEY,
    type INT NOT NULL,
    num_samp INT NOT NULL,
    data_start DATE NOT NULL,
    data_end DATE
);


-- Create the sampl Table
CREATE TABLE sampl (
    id_samp SERIAL PRIMARY KEY,
    id_res INT NOT NULL,
    qrtest TEXT NOT NULL,
    FOREIGN KEY (id_res) REFERENCES reseach(id_res)
);


-- Create the data Table
CREATE TABLE data (
    id_sample SERIAL PRIMARY KEY,
    id_samp INT NOT NULL,
    date DATE NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    temperature INT,
    gps TEXT,
    FOREIGN KEY (id_samp) REFERENCES sampl(id_samp)
);

-- Create the global_counters Table
CREATE TABLE global_counters (
    counter_qr INT NOT NULL,
    counter_research INT NOT NULL
);

-- Initialize the global counters
INSERT INTO global_counters (counter_qr, counter_research) VALUES (0, 0);