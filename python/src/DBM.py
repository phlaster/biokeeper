import sys
sys.path.insert(1, './python/src/DBM')
from UsersManager import UsersManager
from KitsManager import KitsManager
from ResearchesManager import ResearchesManager
from SamplesManager import SamplesManager
from Logger import Logger

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