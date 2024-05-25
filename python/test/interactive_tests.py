import sys
sys.path.append('python/src')
from DBManager import DBManager, LOGDATA

import datetime
import time

DBM = DBManager(LOGDATA, '/dev/null')

# DBM.generate_test_example()
# DBM.generate_test_example()
# DBM.generate_test_example()
# DBM.generate_test_example()
# DBM.generate_test_example()

# DBM.users.new("Artiom", "password")
print(DBM.users.status_of("Artiom"))

# w = DBM.samples.get_weather(3)
# # print(w)

# p = DBM.samples.get_photo(3)
# # print(bytes(p))

# c = DBM.samples.get_info(3)["comment"]
# print(c)