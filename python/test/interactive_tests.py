import sys
sys.path.append('python/src')
from DBManager import DBManager, LOGDATA

DBM = DBManager(LOGDATA, '/dev/null')

w = DBM.samples.get_weather(3)
# print(w)

p = DBM.samples.get_photo(3)
# print(bytes(p))

c = DBM.samples.get_info(3)["comment"]
print(c)