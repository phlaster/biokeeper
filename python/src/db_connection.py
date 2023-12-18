from pathlib import Path
import subprocess

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

    ip, error = process.communicate()
    assert error == '', "Some error occured while deducing the postgres local ip"

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
