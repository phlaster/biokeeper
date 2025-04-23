CREATE OR REPLACE FUNCTION refresh_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_status_n()
RETURNS TRIGGER AS $$
BEGIN
    -- Handle INSERT operation
    IF (TG_OP = 'INSERT') THEN
        EXECUTE format(
            'UPDATE %I AS us
             SET details = ROW((us.details).key, (us.details).info, (us.details).n + 1)::status_info
             WHERE id = $1',
             TG_ARGV[0]
        ) USING NEW.status;
        RETURN NEW;
    END IF;

    -- Handle UPDATE operation
    IF (TG_OP = 'UPDATE') THEN
        -- Decrement the old status if it has changed
        IF (OLD.status IS DISTINCT FROM NEW.status) THEN
            EXECUTE format(
                'UPDATE %I AS us_old
                 SET details = ROW((us_old.details).key, (us_old.details).info, (us_old.details).n - 1)::status_info
                 WHERE id = $1',
                 TG_ARGV[0]
            ) USING OLD.status;
            
            -- Increment the new status
            EXECUTE format(
                'UPDATE %I AS us_new
                 SET details = ROW((us_new.details).key, (us_new.details).info, (us_new.details).n + 1)::status_info
                 WHERE id = $1',
                 TG_ARGV[0]
            ) USING NEW.status;
        END IF;
        RETURN NEW;
    END IF;
    
    IF (TG_OP = 'DELETE') THEN
        EXECUTE format(
            'UPDATE %I AS us
             SET details = ROW((us.details).key, (us.details).info, (us.details).n - 1)::status_info
             WHERE id = $1',
             TG_ARGV[0]
        ) USING OLD.status;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;





CREATE TYPE status_info AS (
    key TEXT,
    info TEXT,
    n INT
);