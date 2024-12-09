CREATE TABLE "user_research" (
    user_id INTEGER NOT NULL,
    research_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, research_id),
    FOREIGN KEY (user_id) REFERENCES "user"(id),
    FOREIGN KEY (research_id) REFERENCES "research"(id));


CREATE TABLE "user_research_pending" (
    user_id INTEGER NOT NULL,
    research_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, research_id),
    FOREIGN KEY (user_id) REFERENCES "user"(id),
    FOREIGN KEY (research_id) REFERENCES "research"(id));