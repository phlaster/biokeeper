"""
c.l. args:
    str no spaces: researchtype
    int: number of samples
    YYYY.MM.DD: start # dot separated!
    YYYY.MM.DD: end
"""
import psycopg2

import sys
from datetime import date

from Research import Research
# sys.path.append('/') # in Docker container db_settings will be mounted at /
from db_settings import db


def str_to_date(s):
    ls = [int(a) for a in s.split('.')]
    return date(*ls)


def connect2db(logdata):
    connection = psycopg2.connect(
        database = logdata["db_name"],
        host =     logdata["db_host"],
        user =     logdata["db_user"],
        password = logdata["db_pass"],
        port =     logdata["db_port"])
    dbhandle = connection.cursor()
    return connection, dbhandle


def update_counter(connection, counter_name, increment) -> None:
    try:
        base = connection.cursor()
        base.execute(f"SELECT {counter_name} FROM global_counters")
        counter = int(base.fetchone()[0])
        counter += increment
        base.execute(f"UPDATE global_counters SET {counter_name} = {str(counter)}")
        print(f"Global counter {counter_name} has been updated by {increment}", file = sys.stderr)
    finally:
        base.close()


def get_offset(connection, counter) -> int:
    try:
        base = connection.cursor()
        base.execute(f"SELECT {counter} FROM global_counters")
        offset = int(base.fetchone()[0])
        return offset
    finally:
        base.close()


def push_qrs(connection, research) -> None:
    try:
        base = connection.cursor()
        qrcodes = research.get_qrs()

        for i in range(research.offset+1, research.offset+1+research.n_samples):
            base.execute("""
                INSERT INTO sampl (id_samp, id_res, qrtest)
                VALUES (%s, %s, %s);
                """,
                (i, research.id, qrcodes[i])
            )
        print(f"{research.n_samples} qr codes have been pushed to db!", file = sys.stderr)
    finally:
        base.close()


def main():
    research_type = sys.argv[1]
    n_samples = int(sys.argv[2])
    data_start = sys.argv[3]
    data_end = sys.argv[4]

    try:
        connection, dbase = connect2db(db)
        offset_qr = get_offset(connection, 'counter_qr')
        update_counter(connection, "counter_qr", n_samples)

        update_counter(connection, "counter_research", 1)
        research_id = get_offset(connection, 'counter_research')


        new_research = Research(
            research_id,
            str_to_date(date_start),
            str_to_date(date_end),
            research_type,
            n_samples,
            offset_qr
        )

        dbase.execute("""
            INSERT INTO reseach (id_res, type, num_samp, data_start, data_end)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (new_research.id, new_research.research_type, new_research.n_samples, new_research.date_start, new_research.date_end)
        )


        push_qrs(connection, new_research)
        new_research.write_codes()
        new_research.write_pictures()

    finally:
        connection.commit()
        dbase.close()
        connection.close()


if __name__ == "__main__":
    try:
        main()
        print(f"Research {research_type} with {n_samples} samples has been added!", file=sys.stderr)
    except OSError as e:
        print(e)
