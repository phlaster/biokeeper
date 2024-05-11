import random
import string
import sys
import traceback
import datetime
from time import time

sys.path.insert(1, './python/src')
import db_connection
from DBManager import DBManager


# Existing statuses
def existing_statuses():
    assert DBM.is_status_of("user", "admin")
    assert DBM.is_status_of("user", "volunteer")
    assert DBM.is_status_of("user", "observer")
    assert not DBM.is_status_of("user", "wrongstatus")

    assert DBM.is_status_of("kit", "created")
    assert DBM.is_status_of("kit", "sent")
    assert DBM.is_status_of("kit", "activated")
    assert not DBM.is_status_of("kit", "wrongstatus")

    assert DBM.is_status_of("research", 'pending')
    assert DBM.is_status_of("research", 'ongoing')
    assert DBM.is_status_of("research", 'paused')
    assert DBM.is_status_of("research", 'ended')
    assert DBM.is_status_of("research", 'cancelled')
    assert not DBM.is_status_of("research", "wrongstatus")

def new_user():
    # Creation
    global user_1_id
    user_1_id = DBM.new_user(username_1, passwd_1)
    assert type(user_1_id) == int
    assert DBM.is_user(username_1)

    # Password match
    assert DBM.is_password_match(username_1, passwd_1)
    assert not DBM.is_password_match(username_1, rstr(11))

    # Status checks
    assert DBM.get_user_status(username_1) == "observer"
    assert not DBM.change_user_status(username_1, "wrongstatus")
    assert DBM.change_user_status(username_1, "admin") == "admin"
    assert DBM.get_user_status(username_1) == "admin"

def user_info():
    # Getting user info
    global user_1_info
    user_1_info = DBM.get_user_info(username_1)
    assert type(user_1_info) == dict
    assert user_1_info["created_at"] < user_1_info["updated_at"]
    assert user_1_info["n_samples_collected"] == 0
    assert user_1_info["user_status"] == DBM.get_user_status(username_1)
    assert user_1_info["user_id"] >= 1
    assert DBM.get_all_users()[username_1] == user_1_info
    assert DBM.n_users() == len(DBM.get_all_users())
    assert DBM.get_user_info(rstr()) == {}

def user_renaming():
    # Changing username
    assert DBM.change_user_name(username_1, username_2) == username_2
    assert not DBM.is_user(username_1)
    assert DBM.is_user(username_2)
    global user_2_info
    user_2_info = DBM.get_user_info(username_2)
    shared_items = {k: user_1_info[k] for k in user_1_info if k in user_2_info and user_1_info[k] == user_2_info[k]}
    assert len(user_2_info) - len(shared_items) == 1
    assert user_1_info["updated_at"] < user_2_info["updated_at"]


    # Password match after renaming
    assert DBM.is_password_match(username_2, passwd_1)
    assert not DBM.is_password_match(username_2, rstr(11))


    # Password match after renaming
    assert DBM.is_password_match(username_2, passwd_1)
    assert not DBM.is_password_match(username_2, rstr(11))

def counting_users():
    # Counting
    assert DBM.n_users() == DBM.n_users("all")
    n_all_users = DBM.n_users()
    assert n_all_users > 0
    n_admins = DBM.n_users("admin")
    assert n_admins >= 1
    n_volunteers = DBM.n_users("volunteer")
    assert n_volunteers >= 0
    n_observers = DBM.n_users("observer")
    assert n_volunteers >= 0
    assert n_admins + n_volunteers + n_observers == n_all_users

    # New user added
    user_3_id = DBM.new_user(username_3, passwd_3)
    assert not user_1_id == user_3_id
    assert DBM.is_user(username_3)
    assert not DBM.is_user(username_3) == DBM.is_user(username_1)

    # Old passwords to new user
    assert DBM.is_password_match(username_3, passwd_3)
    assert not DBM.is_password_match(username_3, passwd_1)
    assert not DBM.is_password_match(username_1, passwd_1)
    assert not DBM.is_password_match(username_2, passwd_3)

    # Counting after user added
    assert n_all_users + 1 == DBM.n_users() == DBM.n_users("all")
    assert n_observers + 1 == DBM.n_users("observer")
    assert n_volunteers == DBM.n_users("volunteer")
    assert n_admins == DBM.n_users("admin")

    # Counting after changing status
    assert DBM.change_user_status(username_3, "volunteer") == "volunteer"
    assert n_observers == DBM.n_users("observer")
    assert n_volunteers + 1 == DBM.n_users("volunteer")
    assert n_admins == DBM.n_users("admin")

    # Counting after changing username
    assert not DBM.change_user_name(username_3, username_2) # already taken
    assert DBM.change_user_name(username_3, username_1) # was free after ranaming
    assert n_observers == DBM.n_users("observer")
    assert n_volunteers + 1 == DBM.n_users("volunteer")
    assert n_admins == DBM.n_users("admin")

def researches():
    research_user = rstr()
    research_user_id = DBM.new_user(research_user, rstr())
    assert DBM.get_user_status(research_user) == "observer"
    
    research_name = rstr()
    day_start = date(2020, 1, 1)
    n_res = DBM.n_researches()

    n_res_pending = DBM.n_researches("pending")
    n_res_ongoing = DBM.n_researches("ongoing")
    assert n_res == DBM.n_researches("all")
    assert n_res_pending >= 0
    assert n_res_ongoing >= 0
    assert n_res_pending + n_res_ongoing <= n_res

    # Research creation
    assert not DBM.new_research(research_name, research_user, day_start) # user has no privilege
    DBM.change_user_status(research_user, "admin")
    assert DBM.new_research(research_name, research_user, day_start)
    assert DBM.is_research(research_name)
    assert not DBM.new_research(research_name, research_user, day_start) # same name collision
    assert DBM.n_researches("all") == n_res + 1
    assert DBM.n_researches("pending") == n_res_pending + 1
    assert DBM.n_researches("ongoing") == n_res_ongoing

    # Changing research status
    research_status = DBM.get_research_status(research_name)
    assert research_status == "pending"
    assert not DBM.change_research_status(research_name, "nonexisting status")
    assert research_status == "pending"
    assert DBM.change_research_status(research_name, "ongoing") == "ongoing"
    assert DBM.get_research_status(research_name) == "ongoing"
    assert DBM.n_researches("all") == n_res + 1
    assert DBM.n_researches("pending") == n_res_pending
    assert DBM.n_researches("ongoing") == n_res_ongoing + 1

    # Research info
    research_info = DBM.get_research_info(research_name)
    assert type(research_info) == dict
    assert research_info["research_id"] >= 1
    assert research_info["research_status"] == DBM.get_research_status(research_name) == "ongoing"
    assert research_info["created_at"] < research_info["updated_at"]
    assert research_info["created_by"] == research_user_id
    assert research_info["n_samples"] == 0
    assert research_info["day_end"] == None
    assert research_info["research_comment"] == None
    assert DBM.get_all_researches()[research_name] == research_info
    assert len(DBM.get_all_researches()) == DBM.n_researches()
    assert DBM.get_research_info(rstr()) == {}

    #changing other columns
    random_comment = rstr(100)
    bad_day_end = date(2019, 1, 1) # less than day_start
    good_day_end = date(2025, 1, 1)

    assert DBM.change_research_comment(research_name, random_comment)
    assert not DBM.change_research_day_end(research_name, bad_day_end)
    assert DBM.change_research_day_end(research_name, good_day_end)

    research_updated_info = DBM.get_research_info(research_name)
    assert research_updated_info["day_end"] == good_day_end
    assert research_updated_info["research_comment"] == random_comment

def kits():
    # Creating
    n_qrs = 10
    kit_id = DBM.new_kit(n_qrs)
    assert kit_id >= 1
    assert DBM.is_kit(kit_id)
    assert not DBM.is_kit(99999999)
    
    # Change status
    assert not DBM.get_kit_status(999999999)
    kit_status = DBM.get_kit_status(kit_id)
    assert DBM.is_status_of("kit", kit_status)
    assert kit_status == "created"
    assert not DBM.change_kit_status(kit_id, "rubbish")
    assert DBM.change_kit_status(kit_id, "sent") == "sent"
    
    # qrs
    assert len(set(DBM.get_kit_qrs(kit_id))) == n_qrs
    kit_new_id = DBM.new_kit(n_qrs)
    assert DBM.is_kit(kit_new_id)
    assert not DBM.get_kit_status(kit_new_id) == DBM.get_kit_status(kit_id)
    assert set(DBM.get_kit_qrs(kit_id)).intersection(set(DBM.get_kit_qrs(kit_new_id))) == set()

    # info
    kit_1_info = DBM.get_kit_info(kit_id)
    kit_2_info = DBM.get_kit_info(kit_new_id)
    print(DBM.get_kit_info(9999999))
    assert DBM.get_kit_info(9999999) == {}
    assert isinstance(kit_1_info, dict) and isinstance(kit_2_info, dict)
    assert not kit_1_info == kit_2_info

    assert isinstance(kit_1_info["kit_unique_code"], bytes)
    assert not kit_1_info["kit_unique_code"] == kit_2_info["kit_unique_code"]
    assert kit_1_info["created_at"] < kit_1_info["updated_at"] < kit_2_info["created_at"] == kit_2_info["updated_at"]
    qr_key = list(kit_1_info["qrs"].keys())[3]
    assert isinstance(qr_key, int)
    qr_bytes = kit_1_info["qrs"][qr_key]
    assert isinstance(qr_bytes, bytes)
    assert DBM.is_qr(qr_bytes)

    # Kit owners
    assert kit_1_info['owner'] == None
    owner_name = rstr()
    owner_id = DBM.new_user(owner_name, rstr())
    assert not DBM.change_kit_owner(kit_id, rstr()) # wrong username
    assert DBM.change_kit_owner(kit_id, owner_name) == kit_id
    assert DBM.get_kit_info(kit_id)['owner'] == {'user_id': owner_id, 'username': owner_name}

def qrcodes():
    new_kit = DBM.new_kit(10)
    qrs = DBM.get_kit_qrs(new_kit)
    assert isinstance(qrs, dict)
    for id in qrs:
        binary = qrs[id]
        assert DBM.is_qr(binary)
        assert not DBM.is_qr(binary)['is_used']
        assert DBM.is_qr(binary)['kit_id'] == new_kit


def samples():
    assert not DBM.new_sample(r'123141143', rstr(), datetime.datetime.now(), (2.4, 2.1))

    research_user = rstr()
    research_user_id = DBM.new_user(research_user, rstr())
    assert DBM.change_user_status(research_user, "admin")
    
    research_name = rstr()
    day_start = datetime.date(2020, 1, 1)
    research_id = DBM.new_research(research_name, research_user, day_start)

    kit_id = DBM.new_kit(5)
    some_qr_bytes = list(DBM.get_kit_qrs(kit_id).values())[2]
    
    assert not DBM.new_sample(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # research is not ongoing
    DBM.change_research_status(research_name, "ongoing")
    assert not DBM.new_sample(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # kit has no owner
    DBM.change_kit_owner(kit_id, research_user)
    assert not DBM.new_sample(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # kit has not been activated
    DBM.change_kit_status(kit_id, "activated")
    sample_id = DBM.new_sample(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1))
    assert isinstance(sample_id, int)
    assert not DBM.new_sample(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # QR is used

logdata = db_connection.DB_LOGDATA
DBM = DBManager(logdata, logfile="test_new.log")
DBM._clear_logs()
DBM.logger.log_message("Info : Test started!")

rstr = lambda k=10: ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))
username_1 = rstr()
passwd_1 = rstr()
username_2 = rstr()
username_3 = rstr()
passwd_3 = rstr()

global test_time
test_time = time()
try:
    # existing_statuses()
    # new_user()
    # user_info()
    # user_renaming()
    # counting_users()
    # researches()
    # kits()
    # qrcodes()
    samples()
    print(f"All tests passed in {round(time()-test_time, ndigits=1)} s.")
except Exception as e:
    _, _, var = sys.exc_info()
    traceback.print_tb(var)
    tb_info = traceback.extract_tb(var)
    filename, line_number, _, text = tb_info[-1]
    DBM.logger.log_message(f"An error occurred on line {line_number} in file {filename} in statement {text}")
    raise e
finally:
    DBM.logger.log_message(f"Info : Test ended in {round(time()-test_time, ndigits=1)} s.")