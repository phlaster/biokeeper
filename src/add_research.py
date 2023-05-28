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
    connection.commit()
    print(f"Global counter has been updated by {increment}", file = stderr)


def main(id, research_type, n_samples, date_start, date_end):
    try:
        connection, dbase = connect2db(db)

        dbase.execute("SELECT * FROM countqr")
        print(int(dbase.fetchone()[0])) # before increment

        update_counter(connection, int(n_samples))
        
        dbase.execute("SELECT * FROM countqr")
        print(int(dbase.fetchone()[0])) # after increment

        
        # n_r = Research(
        #     int(id),
        #     str_to_date(date_start),
        #     str_to_date(date_end),
        #     research_type,
        #     int(n_samples)
        # )

        # dbase.execute("""
        #     INSERT INTO reseach (id_res, type, num_samp, data_start, data_end)
        #     VALUES (%s, %s, %s, %s, %s);
        #     """,
        #     (n_r.id, n_r.research_type, n_r.n_samples, n_r.date_start, n_r.date_end)        
        # )
        # connection.commit()

        # dbase.execute("SELECT * FROM reseach")
        # data = dbase.fetchone()
        # print("This is data:\n", data)


    finally:
        dbase.close()
        connection.close()


if __name__ == "__main__":
    main(argv[1], argv[2], argv[3], argv[4], argv[5])
    print("Fin.")


