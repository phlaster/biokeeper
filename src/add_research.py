"""
Args:
    str no spaces: researchtype
    int: number of samples
    YYYY.MM.DD: start # dot separated!
    YYYY.MM.DD: end
"""
from Research import Research
from settings.db_settings import db
from sys import stderr

from sys import argv
from datetime import date

import psycopg2

def str_to_date(s):
    ls = [int(a) for a in s.split(".")]
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


def update_counter(connection, counter_name, increment):
    try:
        base = connection.cursor()
        base.execute(f"SELECT {counter_name} FROM global_counters")
        counter = int(base.fetchone()[0])
        counter += increment
        base.execute(f"UPDATE global_counters SET {counter_name} = {str(counter)}")
        print(f"Global counter {counter_name} has been updated by {increment}", file = stderr)
    finally:
        base.close()


def get_offset(connection, counter):
    try:
        base = connection.cursor()
        base.execute(f"SELECT {counter} FROM global_counters")
        offset = int(base.fetchone()[0])
        return offset
    finally:
        base.close()


def push_qrs(connection, research):
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
        print(f"{research.n_samples} qr codes have been pushed to db!", file = stderr)
    finally:
        base.close()


def main(research_type, n_samples, date_start, date_end):
    try:
        connection, dbase = connect2db(db)
        offset_qr = get_offset(connection, 'counter_qr')

        update_counter(connection, "counter_research", 1)
        offset_research = get_offset(connection, 'counter_research')
        

        new_research = Research(
            offset_research,
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
        update_counter(connection, "counter_qr", n_samples)


        push_qrs(connection, new_research)
        new_research.write_codes()
        new_research.write_pictures()

    finally:
        connection.commit()
        dbase.close()
        connection.close()


if __name__ == "__main__":
    research_type = argv[1]
    n_samples = int(argv[2])
    data_start, data_end = argv[3], argv[4]

    main(research_type, n_samples, data_start, data_end)

    print(f"Research {research_type} with {n_samples} samples has been added!", file=stderr)
