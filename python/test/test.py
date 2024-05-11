import random
import string
import sys
from datetime import date

sys.path.insert(1, './python/src')
import db_connection
from DBManager import DBManager

logdata = db_connection.DB_LOGDATA
M = DBManager(logdata, logfile="test.log")
# db_manager._clear_logs()

# day_start = date(2024, 1, 31)
# print(M.new_user("Username", "password"))
# print(M.new_research("Research name", "comment", "Username", day_start))
# M.change_user_status("Username", "admin")
# print(M.new_research("Research name", "comment", "Username", day_start))
# print(M.get_research_info("Research name"))
# print(M.get_all_researches())
# print(M.get_research_status("Research name"))
# print(M.change_research_status("Research name", "ongoing"))
# M.change_research_comment("Research name", "Now new comment!")
# print(M.get_research_info("Research name")["research_comment"])
# print(M.get_research_info("Research name")["day_end"])
# wrong_day_end = date(2024, 1, 20)
# M.change_research_day_end("Research name", wrong_day_end)

# correct_day_end = date(2024, 2, 20)
# M.change_research_day_end("Research name", correct_day_end)
# print(M.get_research_info("Research name")["day_end"])

# print(M.is_kit(5))
# print(M.new_kit(10))
# print(M.change_kit_status(1, "sent"))
# print(M.change_kit_status(5, "activated"))
# print(M.change_kit_owner(1, "Username"))
# print(M.get_kit_status(1))
print(M.get_kit_qrs(1)[1][1])
# print(M.get_kit_info(1)["qrs"])
# print(M.get_all_kits())
print(M.is_qr(M.get_kit_qrs(1)[1][1]))

class AlwaysFalseString(str):
    def __new__(cls, value):
        return super(AlwaysFalseString, cls).__new__(cls, value)
    
    def __bool__(self):
        return False

import sys

def n_literal(s):
    return AlwaysFalseString(s)

sys.modules['builtins'].n = n_literal

print(n"hello")
print(n"")
print(n"abc"[0])
print(n"abc" + "def")