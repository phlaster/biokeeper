from pathlib import Path
import subprocess

from colorama import Fore, Style

import psycopg2

def connect2db(logdata):
    connection = psycopg2.connect(
        database = logdata["db_name"],
        host =     logdata["db_host"],
        user =     logdata["db_user"],
        password = logdata["db_pass"],
        port =     logdata["db_port"])
    cursor = connection.cursor()
    return connection, cursor


def is_docker():
    cgroup = Path('/proc/self/cgroup')
    return Path('/.dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text()


ip = "localhost"
if not is_docker():
    command = "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' db_postgres"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    ip, e = process.communicate()
    if e != '':
        print(Fore.RED + "Some error occured while deducing the postgres local ip:" + Style.RESET_ALL)
        print(e)
        print(Fore.BLUE + "Starting server anyway..." + Style.RESET_ALL)

DB = {
    "db_name" : "postgres",
    "db_host" : ip.strip("\n"),
    "db_user" : "postgres",
    "db_pass" : "root",
    "db_port" : 5432
}

DB_from_docker = {
    "db_name" : "postgres",
    "db_host" : "db_postgres",
    "db_user" : "postgres",
    "db_pass" : "root",
    "db_port" : 5432
}

def in_db(db_logdata, qr) -> bool:
    try:
        connection, cursor = connect2db(db_logdata)
        cursor.execute(f"SELECT qr_text FROM generated_qrs WHERE qr_text='{qr}'")
        x = cursor.fetchone()
        return x != None
    finally:
        cursor.close()
        connection.close()


def is_used(db_logdata, qr) -> bool:
    try:
        connection, cursor = connect2db(db_logdata)
        cursor.execute(f"SELECT qr_id FROM generated_qrs WHERE qr_text='{qr}'") # FINDS QR ID for given QR string
        qr_id = int(cursor.fetchone()[0])

        cursor.execute(f"SELECT qr_id FROM collected_samples WHERE qr_id={qr_id}")
        x = cursor.fetchone()
        return x != None
    finally:
        cursor.close()
        connection.close()


def is_expired(db_logdata, qr) -> bool:
    try:
        connection, cursor = connect2db(db_logdata)
        cursor.execute(f"SELECT research_id FROM generated_qrs WHERE qr_text='{qr}'") # FINDS sample ID from QRcode
        research_id = int(cursor.fetchone()[0])
        cursor.execute(f"SELECT day_start, day_end FROM researches WHERE research_id={research_id}")
        date_end = cursor.fetchone()[1]
        return date_end < date.today()
    finally:
        cursor.close()
        connection.close()


def push_request(db_logdata, request) -> None:
    qr = request[0:16]
    req_body = request[17:].split('&')
    temperature = round(float(req_body[0]))
    location = req_body[1].strip('/')

    try:
        connection, cursor = connect2db(db_logdata)
        cursor.execute(f"SELECT qr_id FROM generated_qrs WHERE qr_text='{qr}'")
        qr_id = int(cursor.fetchone()[0])

        cursor.execute("""
            INSERT INTO collected_samples (qr_id, date, time, temperature, gps)
            VALUES (%s, %s, %s, %s, POINT(%s));
            """,
            (qr_id, date.today(), datetime.now(), temperature, location)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()