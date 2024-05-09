"""
C.l. args:
    int: research id
"""

from Research import Research
import sys, os, qrcode
from db_connection import *


def retrieve_qrs(cursor, research_id):
    cursor.execute("""
        SELECT qr_text, qr_id
        FROM generated_qrs
        WHERE research_id = %s
        ORDER BY qr_id ASC
    """, (research_id,))
    return cursor.fetchall()

def write_codes(qrs, research_id):
    research_dir = f"research_{research_id}"
    if not os.path.isdir(research_dir):
        os.makedirs(research_dir)

    N = len(qrs)
    name = research_dir + os.sep + f"research={research_id}" + f"_qr={N}.csv"
    with open(name, "w") as f:
        for (qr, id) in qrs:
            print(f"{id},{qr}", file=f)
    return

def write_pictures(qrs, research_id):
    research_dir = f"research_{research_id}"
    if not os.path.isdir(research_dir):
        os.makedirs(research_dir)

    for (qr, id) in qrs:
        qr_generator = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=25,
            border=2,
        )
        qr_generator.add_data(qr)
        qr_generator.make(fit=True)

        name = research_dir+os.sep+str(id) + ".svg"
        qr_generator.make_image(fill_color="black", back_color="white").save(name)
    return

def main():
    research_id = sys.argv[1]
    with DBConnection(DB_LOGDATA) as (connection, cursor):
        qrs = retrieve_qrs(cursor, research_id)
        if len(qrs) == 0:
            print(f"No entries for research #{research_id} in database!", file=sys.stderr)
            return
        write_codes(qrs, research_id)
        write_pictures(qrs, research_id)
        print(f"Research #{research_id} has been regenerated!", file=sys.stderr)


if __name__ == "__main__":
    main()