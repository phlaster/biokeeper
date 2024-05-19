import sys
sys.path.insert(1, './python/src')

from DBManager import DBManager, LOGDATA

logfile="fastapi.log"
DBM = DBManager(LOGDATA, logfile)
DBM.logger.clear_logs()
DBM.logger.log("Info : Test started!")