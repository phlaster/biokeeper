"""
Args:
    int: id of research
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


def update_counter(connection, increment):
    base = connection.cursor()
    base.execute("SELECT * FROM countqr")
    countqr = int(base.fetchone()[0])
    countqr += increment
    base.execute(f"UPDATE countqr SET qr = {str(countqr)}")
    print(f"Global counter has been updated by {increment}", file = stderr)


def get_offset(connection, value):
    base = connection.cursor()
    base.execute(f"SELECT {value} FROM countqr")
    return int(base.fetchone()[0])


def push_qrs(connection, research):
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


def main(id, research_type, n_samples, date_start, date_end):
    try:
        connection, dbase = connect2db(db)
        offset = get_offset(connection, 'qr')
        
        new_research = Research(
            id,
            str_to_date(date_start),
            str_to_date(date_end),
            research_type,
            n_samples,
            offset
        )

        dbase.execute("""
            INSERT INTO reseach (id_res, type, num_samp, data_start, data_end)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (new_research.id, new_research.research_type, new_research.n_samples, new_research.date_start, new_research.date_end)        
        )
        
        update_counter(connection, n_samples)
        push_qrs(connection, new_research)
        new_research.write_codes()

    finally:
        connection.commit()
        dbase.close()
        connection.close()


if __name__ == "__main__":
    id = int(argv[1])
    research_type = argv[2]
    n_samples = int(argv[3])
    data_start, data_end = argv[4], argv[5]

    main(id, research_type, n_samples, data_start, data_end)

    print("Research {research_type} with id {id} has been added!", file=stderr)
