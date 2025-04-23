from DBM.UsersManager import UsersManager
from DBM.KitsManager import KitsManager
from DBM.ResearchesManager import ResearchesManager
from DBM.SamplesManager import SamplesManager
from Logger import Logger
from Weather import Weather

import random
import string
import datetime
from threading import Thread

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
    "db_host" : "core_db" if in_docker() else POSTGRES_DOCKER_IP
}


class DBManager:
    def __init__(self, logdata, logfile="logs.log"):
        self.logger = Logger(logfile)
        self.users = UsersManager(logdata, logfile=logfile)
        self.kits = KitsManager(logdata, logfile=logfile)
        self.researches = ResearchesManager(logdata, logfile=logfile)
        self.samples = SamplesManager(logdata, logfile=logfile)
        self.weather = Weather(past_days=3)

    def complete_weather_request(self, sample_id, log=False):
        if not self.samples.has(sample_id):
            return self.logger.log(f"Sample #{sample_id} not found") if log else None
        sample_info = self.samples.get_info(sample_id)
        collected_at = datetime.datetime.fromisoformat(sample_info['collected_at'])
        latitude, longitude = map(float, sample_info['gps'].strip("()").split(","))
        weather = self.weather.weather_request((latitude, longitude), collected_at)
        if weather:
            self.samples.push_weather(sample_id, weather, log=log)
        else:
            log and self.logger.log(f"Couldn't fetch the weather data for sample #{sample_id}")


    def generate_test_example(self, log=False):
        with open("python/src/DBM/example/research.md", "r") as f:
            research_comment = f.read()
        with open('python/src/DBM/example/mps', 'rb') as file:
            sample_photo = file.read()
        with open('python/src/DBM/example/sample.md', 'r') as file:
            sample_comment = file.read()

        rstr = lambda k=10: ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))
        user_name = rstr()
        user_password = "password"
        user_id = self.users.new(user_name, user_password, log=log)
        self.users.change_status(user_name, "admin", log=log)

        research_name = rstr()
        day_start = datetime.date(2020, 1, 1)
        research_id = self.researches.new(research_name, user_name, day_start, research_comment=research_comment, log=log)
        self.researches.change_status(research_name, "ongoing", log=log)

        kit_id = self.kits.new(11, log=log)
        self.kits.change_owner(kit_id, user_name, log=log)
        self.kits.change_status(kit_id, "activated", log=log)

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
        
        for key, value in self.kits.get_info(kit_id).items():
            body["kit"][key] = value
        
        qr_hex = list(body["kit"]["qrs"].items())[-1][1]

        sample_id = self.samples.new(qr_hex, research_name, datetime.datetime.now(datetime.timezone.utc), (60.00577, 30.3742), log=True)
        self.samples.push_photo(sample_id, sample_photo, log=log)
        self.samples.push_comment(sample_id, sample_comment, log=log)
        self.complete_weather_request(sample_id, log=log)
        
        body["sample"] = self.samples.get_info(sample_id)
        body["sample"]["id"] = sample_id
        for key, value in self.researches.get_info(research_name).items():
            body["research"][key] = value
        for key, value in self.users.get_info(user_name).items():
            body["user"][key] = value

        log and self.logger.log(f"Info : Test example generated: user #{user_id}, research #{research_id}, kit #{kit_id}, sample #{sample_id}")
        return body
