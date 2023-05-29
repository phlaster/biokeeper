"""
C.l. args:
    int: research id
"""

from Research import Research
from settings.db_settings import db
from sys import argv
from add_research import connect2db


def date_to_str(d):
    return '.'.join(str(d).split("-"))


def extract_research_params(connection, id):
    try:
        base = connection.cursor()
        base.execute(f"SELECT * FROM reseach WHERE id_res={id}")
        got = base.fetchone()
        assert got != None, f"No research with id {id} was found!" 

        base.execute("SELECT COUNT(*) FROM sampl WHERE id_res < %s", (id,))
        offset = int(base.fetchone()[0])

        
        extracted = (
            int(got[0]),
            date_to_str(got[3]),
            date_to_str(got[4]),
            got[1],
            int(got[2]),
            offset
        )
        return extracted
    finally:
        base.close()
    


def main():
    try:
        connection, dbase = connect2db(db)
        params = extract_research_params(connection, argv[1])
        r = Research(*params)
        r.write_codes()
        r.write_pictures()

    finally:
        dbase.close()
        connection.close()


if __name__ == "__main__":
    main()