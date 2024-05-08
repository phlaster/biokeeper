from pathlib import Path
import subprocess

from colorama import Fore, Style
from datetime import date
import psycopg2

# object that supports the context manager protocol (with ... as ...:)
class DBConnection:
    def __init__(self, logdata):
        self.logdata = logdata
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = psycopg2.connect(
            database=self.logdata["db_name"],
            host=self.logdata["db_host"],
            user=self.logdata["db_user"],
            password=self.logdata["db_pass"],
            port=self.logdata["db_port"]
        )
        self.cursor = self.connection.cursor()
        return self.connection, self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()


# Checks, if the script runs inside a container or
# (for debugging purposes) from the console
def is_docker():
    cgroup = Path('/proc/self/cgroup')
    return Path('/.dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text()


def in_db(db_logdata, qr) -> bool:
    with DBConnection(db_logdata) as (connection, cursor):
        cursor.execute(f"SELECT qr_text FROM generated_qrs WHERE qr_text='{qr}'")
        return cursor.fetchone() is not None


def is_used(db_logdata, qr) -> bool:
    with DBConnection(db_logdata) as (connection, cursor):
        cursor.execute(f"SELECT qr_id FROM generated_qrs WHERE qr_text='{qr}'")
        qr_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT qr_id FROM collected_samples WHERE qr_id={qr_id}")
        return cursor.fetchone() is not None


def is_expired(db_logdata, qr) -> bool:
    with DBConnection(db_logdata) as (connection, cursor):
        cursor.execute(f"SELECT research_id FROM generated_qrs WHERE qr_text='{qr}'")
        research_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT day_end FROM researches WHERE research_id={research_id}")
        date_end = cursor.fetchone()[0]
        return date_end < date.today()


def push_request(db_logdata, request) -> None:
    qr, req_body = request[:16], request[17:].split('&')
    temperature = round(float(req_body[0]))
    location = req_body[1].strip('/')

    with DBConnection(db_logdata) as (connection, cursor):
        cursor.execute(f"SELECT qr_id FROM generated_qrs WHERE qr_text='{qr}'")
        qr_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO collected_samples (qr_id, date, time, temperature, gps)
            VALUES (%s, %s, %s, %s, POINT(%s));
            """,
            (qr_id, date.today(), datetime.now(), temperature, location)
        )
        connection.commit()


"""
Code below checks, if the server is being stratred inside
docker container or outside and in either case it deduces
the ip of the database (which has to be up and running in
a container anyway) 
"""
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

# DB_LOGDATA will be exported to serv_SIMPLE.py
DB_LOGDATA = DB_from_docker if is_docker() else DB