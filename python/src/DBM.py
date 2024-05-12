import sys
sys.path.insert(1, './python/src/DBM')
from UsersManager import UsersManager
from KitsManager import KitsManager
from ResearchesManager import ResearchesManager
from SamplesManager import SamplesManager
from Logger import Logger

class DBManager:
    def __init__(self, logdata, logfile="logs.log"):
        self.logger = Logger(logfile)
        self.users = UsersManager(logdata, logfile="logs.log")
        self.kits = KitsManager(logdata, logfile="logs.log")
        self.researches = ResearchesManager(logdata, logfile="logs.log")
        self.samples = SamplesManager(logdata, logfile="logs.log")