import sys

sys.path.insert(1, './python/src')
sys.path.insert(1, './python/src/DBM')
from db_connection import DB_LOGDATA as logdata
from DBM import DBManager

logfile="fastapi.log"
DBM = DBManager(logdata, logfile)
DBM.logger.clear_logs()
DBM.logger.log_message("Info : Test started!")