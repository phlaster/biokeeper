import random
import string
import sys
import traceback
import datetime
from time import time

sys.path.insert(1, './python/src')
sys.path.insert(1, './python/src/DBM')
from db_connection import DB_LOGDATA as logdata
from DBM import DBManager
# from UsersManager import UsersManager
# from KitsManager import KitsManager
# from ResearchesManager import ResearchesManager
# from SamplesManager import SamplesManager


# Existing statuses
def existing_statuses():
    assert DBM.users.has_status("admin")
    assert DBM.users.has_status("volunteer")
    assert DBM.users.has_status("observer")
    assert not DBM.users.has_status("wrongstatus")

    assert DBM.kits.has_status("created")
    assert DBM.kits.has_status("sent")
    assert DBM.kits.has_status("activated")
    assert not DBM.kits.has_status("wrongstatus")

    assert DBM.researches.has_status('pending')
    assert DBM.researches.has_status('ongoing')
    assert DBM.researches.has_status('paused')
    assert DBM.researches.has_status('ended')
    assert DBM.researches.has_status('cancelled')
    assert not DBM.researches.has_status("wrongstatus")

def new_user():
    # Creation
    global user_1_id
    user_1_id = DBM.users.new(user_name_1, passwd_1)
    assert type(user_1_id) == int
    assert DBM.users.has(user_name_1)

    # Password match
    assert DBM.users.password_match(user_name_1, passwd_1)
    assert not DBM.users.password_match(user_name_1, rstr(11))

    # Status checks
    assert DBM.users.status_of(user_name_1) == "observer"
    assert not DBM.users.change_status(user_name_1, "wrongstatus")
    assert DBM.users.change_status(user_name_1, "admin") == "admin"
    assert DBM.users.status_of(user_name_1) == "admin"

def user_info():
    # Getting user info
    global user_1_info
    user_1_info = DBM.users.get_info(user_name_1)
    assert type(user_1_info) == dict
    assert user_1_info["created_at"] < user_1_info["updated_at"]
    assert user_1_info["n_samples_collected"] == 0
    assert user_1_info["user_status"] == DBM.users.status_of(user_name_1)
    assert user_1_info["user_id"] >= 1
    assert DBM.users.get_all()[user_name_1] == user_1_info
    assert DBM.users.count() == len(DBM.users.get_all())
    assert DBM.users.get_info(rstr()) == {}

def user_renaming():
    # Changing user_name
    assert DBM.users.change_name(user_name_1, user_name_2) == user_name_2
    assert not DBM.users.has(user_name_1)
    assert DBM.users.has(user_name_2)
    global user_2_info
    user_2_info = DBM.users.get_info(user_name_2)
    shared_items = {k: user_1_info[k] for k in user_1_info if k in user_2_info and user_1_info[k] == user_2_info[k]}
    assert len(user_2_info) - len(shared_items) == 1
    assert user_1_info["updated_at"] < user_2_info["updated_at"]


    # Password match after renaming
    assert DBM.users.password_match(user_name_2, passwd_1)
    assert not DBM.users.password_match(user_name_2, rstr(11))


    # Password match after renaming
    assert DBM.users.password_match(user_name_2, passwd_1)
    assert not DBM.users.password_match(user_name_2, rstr(11))

def counting_users():
    # Counting
    assert DBM.users.count() == DBM.users.count("all")
    n_all_users = DBM.users.count()
    assert n_all_users > 0
    n_admins = DBM.users.count("admin")
    assert n_admins >= 1
    n_volunteers = DBM.users.count("volunteer")
    assert n_volunteers >= 0
    n_observers = DBM.users.count("observer")
    assert n_volunteers >= 0
    assert n_admins + n_volunteers + n_observers == n_all_users

    # New user added
    user_3_id = DBM.users.new(user_name_3, passwd_3)
    assert not user_1_id == user_3_id
    assert DBM.users.has(user_name_3)
    assert not DBM.users.has(user_name_3) == DBM.users.has(user_name_1)

    # Old passwords to new user
    assert DBM.users.password_match(user_name_3, passwd_3)
    assert not DBM.users.password_match(user_name_3, passwd_1)
    assert not DBM.users.password_match(user_name_1, passwd_1)
    assert not DBM.users.password_match(user_name_2, passwd_3)

    # Counting after user added
    assert n_all_users + 1 == DBM.users.count() == DBM.users.count("all")
    assert n_observers + 1 == DBM.users.count("observer")
    assert n_volunteers == DBM.users.count("volunteer")
    assert n_admins == DBM.users.count("admin")

    # Counting after changing status
    assert DBM.users.change_status(user_name_3, "volunteer") == "volunteer"
    assert n_observers == DBM.users.count("observer")
    assert n_volunteers + 1 == DBM.users.count("volunteer")
    assert n_admins == DBM.users.count("admin")

    # Counting after changing user_name
    assert not DBM.users.change_name(user_name_3, user_name_2) # already taken
    assert DBM.users.change_name(user_name_3, user_name_1) # was free after ranaming
    assert n_observers == DBM.users.count("observer")
    assert n_volunteers + 1 == DBM.users.count("volunteer")
    assert n_admins == DBM.users.count("admin")

def researches():
    research_user = rstr()
    research_user_id = DBM.users.new(research_user, rstr())
    assert DBM.users.status_of(research_user) == "observer"
    
    research_name = rstr()
    day_start = datetime.date(2020, 1, 1)
    n_res = DBM.researches.count()

    n_res_pending = DBM.researches.count("pending")
    n_res_ongoing = DBM.researches.count("ongoing")
    assert n_res == DBM.researches.count("all")
    assert n_res_pending >= 0
    assert n_res_ongoing >= 0
    assert n_res_pending + n_res_ongoing <= n_res

    # Research creation
    assert not DBM.researches.new(research_name, research_user, day_start) # user has no privilege
    DBM.users.change_status(research_user, "admin")
    assert DBM.researches.new(research_name, research_user, day_start)
    assert DBM.researches.has(research_name)
    assert not DBM.researches.new(research_name, research_user, day_start) # same name collision
    assert DBM.researches.count("all") == n_res + 1
    assert DBM.researches.count("pending") == n_res_pending + 1
    assert DBM.researches.count("ongoing") == n_res_ongoing

    # Changing research status
    research_status = DBM.researches.status_of(research_name)
    assert research_status == "pending"
    assert not DBM.researches.change_status(research_name, "nonexisting status")
    assert research_status == "pending"
    assert DBM.researches.change_status(research_name, "ongoing") == "ongoing"
    assert DBM.researches.status_of(research_name) == "ongoing"
    assert DBM.researches.count("all") == n_res + 1
    assert DBM.researches.count("pending") == n_res_pending
    assert DBM.researches.count("ongoing") == n_res_ongoing + 1

    # Research info
    research_info = DBM.researches.get_info(research_name)
    assert type(research_info) == dict
    assert research_info["research_id"] >= 1
    assert research_info["research_status"] == DBM.researches.status_of(research_name) == "ongoing"
    assert research_info["created_at"] < research_info["updated_at"]
    assert research_info["created_by"] == research_user_id
    assert research_info["n_samples"] == 0
    assert research_info["day_end"] == None
    assert research_info["research_comment"] == None
    assert DBM.researches.get_all()[research_name] == research_info
    assert len(DBM.researches.get_all()) == DBM.researches.count()
    assert DBM.researches.get_info(rstr()) == {}

    #changing other columns
    random_comment = rstr(100)
    bad_day_end = datetime.date(2019, 1, 1) # less than day_start
    good_day_end = datetime.date(2025, 1, 1)

    assert DBM.researches.change_comment(research_name, random_comment)
    assert not DBM.researches.change_day_end(research_name, bad_day_end)
    assert DBM.researches.change_day_end(research_name, good_day_end)

    research_updated_info = DBM.researches.get_info(research_name)
    assert research_updated_info["day_end"] == good_day_end
    assert research_updated_info["research_comment"] == random_comment

def kits():
    # Creating
    n_qrs = 10
    kit_id = DBM.kits.new(n_qrs)
    assert kit_id >= 1
    assert DBM.kits.has(kit_id)
    assert not DBM.kits.has(99999999)
    
    # Change status
    assert not DBM.kits.status_of(999999999)
    kit_status = DBM.kits.status_of(kit_id)
    assert DBM.kits.has_status(kit_status)
    assert kit_status == "created"
    assert not DBM.kits.change_status(kit_id, "rubbish")
    assert not DBM.kits.change_status(-1, "rubbish")
    assert DBM.kits.change_status(kit_id, "sent") == "sent"
    
    # qrs
    assert len(set(DBM.kits.get_qrs(kit_id))) == n_qrs
    kit_new_id = DBM.kits.new(n_qrs)
    assert DBM.kits.has(kit_new_id)
    assert not DBM.kits.status_of(kit_new_id) == DBM.kits.status_of(kit_id)
    assert set(DBM.kits.get_qrs(kit_id)).intersection(set(DBM.kits.get_qrs(kit_new_id))) == set()

    # info
    kit_1_info = DBM.kits.get_info(kit_id)
    kit_2_info = DBM.kits.get_info(kit_new_id)
    assert DBM.kits.get_info(9999999) == {}
    assert isinstance(kit_1_info, dict) and isinstance(kit_2_info, dict)
    assert not kit_1_info == kit_2_info

    assert isinstance(kit_1_info["kit_unique_code"], bytes)
    assert not kit_1_info["kit_unique_code"] == kit_2_info["kit_unique_code"]
    assert kit_1_info["created_at"] < kit_1_info["updated_at"] < kit_2_info["created_at"] == kit_2_info["updated_at"]
    qr_key = list(kit_1_info["qrs"].keys())[3]
    assert isinstance(qr_key, int)
    qr_bytes = kit_1_info["qrs"][qr_key]
    assert isinstance(qr_bytes, bytes)
    assert DBM.kits.get_qr_info(qr_bytes)

    # Kit owners
    assert kit_1_info['owner'] == None
    owner_name = rstr()
    owner_id = DBM.users.new(owner_name, rstr())
    assert not DBM.kits.change_owner(kit_id, rstr()) # wrong user_name
    assert DBM.kits.change_owner(kit_id, owner_name) == kit_id
    assert DBM.kits.get_info(kit_id)['owner'] == {'user_id': owner_id, 'user_name': owner_name}

def qrcodes():
    new_kit = DBM.kits.new(10)
    qrs = DBM.kits.get_qrs(new_kit)
    assert isinstance(qrs, dict)
    for id in qrs:
        binary = qrs[id]
        assert DBM.kits.get_qr_info(binary)
        assert not DBM.kits.get_qr_info(binary)['is_used']
        assert DBM.kits.get_qr_info(binary)['kit_id'] == new_kit


def samples():
    assert not DBM.samples.new(r'123141143', rstr(), datetime.datetime.now(), (2.4, 2.1))

    research_user = rstr()
    research_user_id = DBM.users.new(research_user, rstr())
    assert DBM.users.change_status(research_user, "admin")
    
    research_name = rstr()
    day_start = datetime.date(2020, 1, 1)
    research_id = DBM.researches.new(research_name, research_user, day_start)

    kit_id = DBM.kits.new(5)
    some_qr_bytes = list(DBM.kits.get_qrs(kit_id).values())[2]
    
    assert not DBM.samples.new(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # research is not ongoing
    DBM.researches.change_status(research_name, "ongoing")
    assert not DBM.samples.new(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # kit has no owner
    DBM.kits.change_owner(kit_id, research_user)
    assert not DBM.samples.new(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # kit has not been activated
    DBM.kits.change_status(kit_id, "activated")

    n_collected = DBM.users.get_info(research_user)["n_samples_collected"]
    assert not DBM.kits.get_qr_info(some_qr_bytes)["is_used"]

    n_samples = DBM.samples.count()
    n_samples_collected = DBM.samples.count("collected")
    n_samples_sent = DBM.samples.count("sent")
    n_samples_delivered = DBM.samples.count("delivered")
    assert n_samples == DBM.samples.count("all")
    assert n_samples_delivered + n_samples_sent + n_samples_collected == n_samples

    sample_id = DBM.samples.new(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # the PUSH
    assert isinstance(sample_id, int)
    assert DBM.users.get_info(research_user)["n_samples_collected"] == n_collected + 1 == 1
    assert DBM.kits.get_qr_info(some_qr_bytes)["is_used"]
    assert not DBM.samples.new(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # QR is used

    assert n_samples + 1 == DBM.samples.count("all")
    assert DBM.samples.count("collected") == n_samples_collected + 1

    assert DBM.samples.has(sample_id)
    assert not DBM.samples.has(sample_id+1)

    assert DBM.samples.has_status("collected")
    assert DBM.samples.has_status("sent")
    assert DBM.samples.has_status("delivered")
    assert not DBM.samples.has_status("lost")

    assert DBM.samples.status_of(sample_id) == "collected"
    assert not DBM.samples.change_status(sample_id, "rubbish")
    assert DBM.samples.status_of(sample_id) == "collected"
    assert DBM.samples.change_status(sample_id, "sent")
    assert DBM.samples.status_of(sample_id) == "sent"
    assert DBM.samples.count("sent") == n_samples_sent + 1
    assert n_samples + 1 == DBM.samples.count("all")

    print(DBM.samples.get_info(sample_id))






logfile="test_strange.log"
DBM = DBManager(logdata, logfile)
DBM.logger.clear_logs()
DBM.logger.log_message("Info : Test started!")

rstr = lambda k=10: ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))
user_name_1 = rstr()
passwd_1 = rstr()
user_name_2 = rstr()
user_name_3 = rstr()
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