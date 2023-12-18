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
from db_connection import connect2db, DB


def str_to_date(s):
    ls = [int(a) for a in s.split('.')]
    return date(*ls)


def update_counter(cursor, counter_name, increment) -> None:
    cursor.execute(f"SELECT {counter_name} FROM global_counters")
    counter = int(cursor.fetchone()[0])
    counter += increment
    cursor.execute(f"UPDATE global_counters SET {counter_name} = {str(counter)}")


def get_offset(cursor, counter) -> int:
    cursor.execute(f"SELECT {counter} FROM global_counters")
    offset = int(cursor.fetchone()[0])
    return offset



def push_qrs(DB_logdata, research) -> None:
    try:
        connection, cursor = connect2db(DB_logdata)
        qrcodes = research.get_qrs()

        for i in range(research.offset+1, research.offset+1+research.n_samples):
            cursor.execute("""
                INSERT INTO generated_qrs (qr_id, research_id, qr_text)
                VALUES (%s, %s, %s);
                """,
                (i, research.research_id, qrcodes[i])
            )
        connection.commit()

        print(f"{research.n_samples} qr codes have been pushed to db!", file = sys.stderr)
    finally:
        cursor.close()
        connection.close()


def offsets(DB_logdata):
    try:
        connection, cursor = connect2db(DB_logdata)
        research_id = get_offset(cursor, 'counter_research')
        offset_qr = get_offset(cursor, 'counter_qr')
        return (research_id, offset_qr)
    finally:
        cursor.close()
        connection.close()


def push_research(DB_logdata, research):
    try:
        connection, cursor = connect2db(DB_logdata)
        cursor.execute("""
            INSERT INTO researches (research_id, research_type, num_samp, day_start, day_end)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (research.research_id, research.research_type, research.n_samples, research.day_start, research.day_end)
        )
        update_counter(cursor, "counter_qr", research.n_samples)
        update_counter(cursor, "counter_research", 1)
        connection.commit()

        print(f"Global counter counter_qr has been updated by {research.n_samples}", file = sys.stderr)
        print(f"Global counter counter_research has been updated by 1", file = sys.stderr)
        print(f"Research #{research.research_id} of type {research.research_type} with {research.n_samples} samples has been added!", file=sys.stderr)
    finally:
        cursor.close()
        connection.close()



def main():
    research_type = int(sys.argv[1])
    n_qrs = int(sys.argv[2])
    day_start = str_to_date(sys.argv[3])
    day_end = str_to_date(sys.argv[4])

    offset_research, offset_qr = offsets(DB)

    new_research = Research(
        offset_research+1,
        day_start,
        day_end,
        research_type,
        n_qrs,
        offset_qr
    )

    push_research(DB, new_research)
    push_qrs(DB, new_research)

    new_research.write_codes()
    new_research.write_pictures()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
