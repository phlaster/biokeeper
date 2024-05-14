from DBM.UsersManager import UsersManager
from DBM.KitsManager import KitsManager
from DBM.ResearchesManager import ResearchesManager
from DBM.SamplesManager import SamplesManager
from Logger import Logger
import random
import string
import datetime

from pathlib import Path

def in_docker():
    cgroup = Path('/proc/self/cgroup')
    return Path('/.dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text()

# Specified in docker-compose.yml
# Hope no collisions will emerge ^^>
POSTGRES_DOCKER_IP = "172.25.0.10"

LOGDATA = {
    "db_name" : "postgres",
    "db_user" : "postgres",
    "db_pass" : "root",
    "db_port" : 5432,
    "db_host" : "db_postgres" if in_docker() else POSTGRES_DOCKER_IP
}


class DBManager:
    """
    Wrapper class for all the specialist managers.
    If the transaction failed, returns value, that Pyhton converts to False
    
    Common methods:
    
        .new(*args, **kwargs) -> int
    Pushes new entry to chosen table.
    Returns unique id of the entry
    
    
        .count(status: str) -> int
    Returns number of entries with given status


        .has_status(status: str) -> tuple
    Checks if given status is valid.
    Returns tuple (status_key: str, status_description: str) or ()


        .has(identifier: str) -> int
    Checks if the table has the entry, specified by identifier
    Returns unique id of the entry or zero

    
        .status_of(identifier) -> str
    Returns status_key string or "" if wrong identifier

    
        .get_info(identifier) -> dict
    Returns dict with object properties or {}

    
        .get_all() -> dict
    Returns dict with keys: unique identifiers and vals: dicts of `.get_info` method or {}

    
        .change_status(identifier, new_status) -> str
    Returns new status string or ""


        .clear_logs() -> None
    Flushes the logfile


        .get_qr_info(qr_bytes: bytes) -> dict
    returns dict with info about qr with given unique bytes or {}
    {'qr_id': int, 'is_used': bool, 'kit_id': int}
    """
    def __init__(self, logdata, logfile="logs.log"):
        self.logger = Logger(logfile)
        self.users = UsersManager(logdata, logfile="logs.log")
        self.kits = KitsManager(logdata, logfile="logs.log")
        self.researches = ResearchesManager(logdata, logfile="logs.log")
        self.samples = SamplesManager(logdata, logfile="logs.log")
    
    def generate_test_example(self):
        rstr = lambda k=10: ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))
        user_name = rstr()
        user_password = rstr()
        self.users.new(user_name, user_password)
        self.users.change_status(user_name, "admin")

        research_name = rstr()
        day_start = datetime.date(2020, 1, 1)
        self.researches.new(research_name, user_name, day_start)

        kit_id = self.kits.new(11)
        self.kits.change_owner(kit_id, user_name)
        self.kits.change_status(kit_id, "activated")

        body = {
            "user" : {
                "name" : user_name,
                "password" : user_password
            },
            "research" : {
                "name" : research_name
            },
            "kit" : {
                "id" : kit_id
            }
        }
        
        for key, value in self.users.get_info(user_name).items():
            body["user"][key] = value
        for key, value in self.kits.get_info(kit_id).items():
            body["kit"][key] = value
        for key, value in self.researches.get_info(research_name).items():
            body["research"][key] = value
        
        qr_hex = list(body["kit"]["qrs"].items())[-1][1]

        sample_id = self.samples.new(qr_hex, research_name, datetime.datetime.now(), (4.2, 6.9))
        print(sample_id)
        return
        with open('python/src/DBM/mps', 'rb') as file:
            photo_bytes = file.read()
            self.samples.push_photo(sample_id, photo_bytes)

        body["sample"] = self.samples.get_info(sample_id)
        return body