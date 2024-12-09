-- 01_user.sql

CREATE TABLE user_role (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    info TEXT
);

INSERT INTO user_role (name, info) VALUES
    ('observer', 'Default status for new users'),
    ('volunteer', 'User has contributed to researches'),
    ('admin', 'User has administrative privileges');


CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    last_password_update TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    role_id INT REFERENCES user_role(id)  NOT NULL DEFAULT 1 -- Внешний ключ для роли пользователя
);

CREATE OR REPLACE FUNCTION update_last_password_update()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.password_hash IS DISTINCT FROM OLD.password_hash THEN
        NEW.last_password_update := CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER update_last_password_trigger
BEFORE INSERT OR UPDATE ON "user"
FOR EACH ROW
EXECUTE FUNCTION update_last_password_update();

