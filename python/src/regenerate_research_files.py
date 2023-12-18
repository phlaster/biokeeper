"""
C.l. args:
    int: research id
"""

from Research import Research
import sys
from db_connection import connect2db, DB


def date_to_str(d) -> str:
    return '.'.join(str(d).split("-"))


def extract_research_params(connection, id) -> tuple:
    try:
        base = connection.cursor()
        base.execute(f"SELECT * FROM researches WHERE research_id={id}")
        extracted = base.fetchone()

        assert extracted != None, f"No research with id {id} was found!"

        research_id = int(extracted[0])
        day_start = date_to_str(extracted[3])
        day_end = date_to_str(extracted[4])
        research_type = int(extracted[1])
        n_samples = int(extracted[2])

        base.execute("SELECT COUNT(*) FROM generated_qrs WHERE research_id < %s", (id,))
        qr_offset = int(base.fetchone()[0])

        params = (
            research_id,
            day_start,
            day_end,
            research_type,
            n_samples,
            qr_offset
        )

        return params
    finally:
        base.close()


def main():
    try:
        research_id = sys.argv[1]

        connection, dbase = connect2db(DB)
        params = extract_research_params(connection, research_id)
        r = Research(*params)
        r.write_codes()
        r.write_pictures()

    finally:
        dbase.close()
        connection.close()


if __name__ == "__main__":
    try:
        main()
        print(f"Research has been regenerated!", file=sys.stderr)

    except e:
        print(e)