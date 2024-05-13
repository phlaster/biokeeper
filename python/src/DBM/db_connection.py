from pathlib import Path
import subprocess

from colorama import Fore, Style
from datetime import date
from DBConnection import DBConnection 

# Checks, if the script runs inside a container or
# (for debugging purposes) from the console
def is_docker():
    cgroup = Path('/proc/self/cgroup')
    return Path('/.dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text()


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