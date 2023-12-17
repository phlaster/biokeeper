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
from db_settings import DB
from db_connection import connect2db


def str_to_date(s):
    ls = [int(a) for a in s.split('.')]
    return date(*ls)


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
                INSERT INTO generated_qrs (qr_id, research_id, qr_text)
                VALUES (%s, %s, %s);
                """,
                (i, research.research_id, qrcodes[i])
            )
        print(f"{research.n_samples} qr codes have been pushed to db!", file = sys.stderr)
    finally:
        base.close()


def main():
    research_type = int(sys.argv[1])
    n_samples = int(sys.argv[2])
    day_start = sys.argv[3]
    day_end = sys.argv[4]

    try:
        connection, dbase = connect2db(DB)
        offset_qr = get_offset(connection, 'counter_qr')
        update_counter(connection, "counter_qr", n_samples)

        update_counter(connection, "counter_research", 1)
        research_id = get_offset(connection, 'counter_research')


        new_research = Research(
            research_id,
            str_to_date(day_start),
            str_to_date(day_end),
            research_type,
            n_samples,
            offset_qr
        )

        dbase.execute("""
            INSERT INTO reseaches (research_id, research_type, num_samp, day_start, day_end)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (new_research.research_id, new_research.research_type, new_research.n_samples, new_research.day_start, new_research.day_end)
        )


        push_qrs(connection, new_research)
        new_research.write_codes()
        new_research.write_pictures()
        print(f"Research #{research_id} of type {research_type} with {n_samples} samples has been added!", file=sys.stderr)

    finally:
        connection.commit()
        dbase.close()
        connection.close()


if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print(e)
