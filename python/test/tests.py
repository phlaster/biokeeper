import random
import string
import sys
import traceback
import datetime
from time import time

sys.path.insert(1, './python/src')
import db_connection
from UsersManager import UsersManager
from KitsManager import KitsManager
from ResearchesManager import ResearchesManager
from SamplesManager import SamplesManager


# Existing statuses
def existing_statuses():
    assert UM.has_status("admin")
    assert UM.has_status("volunteer")
    assert UM.has_status("observer")
    assert not UM.has_status("wrongstatus")

    assert KM.has_status("created")
    assert KM.has_status("sent")
    assert KM.has_status("activated")
    assert not KM.has_status("wrongstatus")

    assert RM.has_status('pending')
    assert RM.has_status('ongoing')
    assert RM.has_status('paused')
    assert RM.has_status('ended')
    assert RM.has_status('cancelled')
    assert not RM.has_status("wrongstatus")

def new_user():
    # Creation
    global user_1_id
    user_1_id = UM.new(username_1, passwd_1)
    assert type(user_1_id) == int
    assert UM.has(username_1)

    # Password match
    assert UM.password_match(username_1, passwd_1)
    assert not UM.password_match(username_1, rstr(11))

    # Status checks
    assert UM.status_of(username_1) == "observer"
    assert not UM.change_status(username_1, "wrongstatus")
    assert UM.change_status(username_1, "admin") == "admin"
    assert UM.status_of(username_1) == "admin"

def user_info():
    # Getting user info
    global user_1_info
    user_1_info = UM.get_info(username_1)
    assert type(user_1_info) == dict
    assert user_1_info["created_at"] < user_1_info["updated_at"]
    assert user_1_info["n_samples_collected"] == 0
    assert user_1_info["user_status"] == UM.status_of(username_1)
    assert user_1_info["user_id"] >= 1
    assert UM.get_all()[username_1] == user_1_info
    assert UM.count() == len(UM.get_all())
    assert UM.get_info(rstr()) == {}

def user_renaming():
    # Changing username
    assert UM.change_name(username_1, username_2) == username_2
    assert not UM.has(username_1)
    assert UM.has(username_2)
    global user_2_info
    user_2_info = UM.get_info(username_2)
    shared_items = {k: user_1_info[k] for k in user_1_info if k in user_2_info and user_1_info[k] == user_2_info[k]}
    assert len(user_2_info) - len(shared_items) == 1
    assert user_1_info["updated_at"] < user_2_info["updated_at"]


    # Password match after renaming
    assert UM.password_match(username_2, passwd_1)
    assert not UM.password_match(username_2, rstr(11))


    # Password match after renaming
    assert UM.password_match(username_2, passwd_1)
    assert not UM.password_match(username_2, rstr(11))

def counting_users():
    # Counting
    assert UM.count() == UM.count("all")
    n_all_users = UM.count()
    assert n_all_users > 0
    n_admins = UM.count("admin")
    assert n_admins >= 1
    n_volunteers = UM.count("volunteer")
    assert n_volunteers >= 0
    n_observers = UM.count("observer")
    assert n_volunteers >= 0
    assert n_admins + n_volunteers + n_observers == n_all_users

    # New user added
    user_3_id = UM.new(username_3, passwd_3)
    assert not user_1_id == user_3_id
    assert UM.has(username_3)
    assert not UM.has(username_3) == UM.has(username_1)

    # Old passwords to new user
    assert UM.password_match(username_3, passwd_3)
    assert not UM.password_match(username_3, passwd_1)
    assert not UM.password_match(username_1, passwd_1)
    assert not UM.password_match(username_2, passwd_3)

    # Counting after user added
    assert n_all_users + 1 == UM.count() == UM.count("all")
    assert n_observers + 1 == UM.count("observer")
    assert n_volunteers == UM.count("volunteer")
    assert n_admins == UM.count("admin")

    # Counting after changing status
    assert UM.change_status(username_3, "volunteer") == "volunteer"
    assert n_observers == UM.count("observer")
    assert n_volunteers + 1 == UM.count("volunteer")
    assert n_admins == UM.count("admin")

    # Counting after changing username
    assert not UM.change_name(username_3, username_2) # already taken
    assert UM.change_name(username_3, username_1) # was free after ranaming
    assert n_observers == UM.count("observer")
    assert n_volunteers + 1 == UM.count("volunteer")
    assert n_admins == UM.count("admin")

def researches():
    research_user = rstr()
    research_user_id = UM.new(research_user, rstr())
    assert UM.status_of(research_user) == "observer"
    
    research_name = rstr()
    day_start = datetime.date(2020, 1, 1)
    n_res = RM.count()

    n_res_pending = RM.count("pending")
    n_res_ongoing = RM.count("ongoing")
    assert n_res == RM.count("all")
    assert n_res_pending >= 0
    assert n_res_ongoing >= 0
    assert n_res_pending + n_res_ongoing <= n_res

    # Research creation
    assert not RM.new(research_name, research_user, day_start) # user has no privilege
    UM.change_status(research_user, "admin")
    assert RM.new(research_name, research_user, day_start)
    assert RM.has(research_name)
    assert not RM.new(research_name, research_user, day_start) # same name collision
    assert RM.count("all") == n_res + 1
    assert RM.count("pending") == n_res_pending + 1
    assert RM.count("ongoing") == n_res_ongoing

    # Changing research status
    research_status = RM.status_of(research_name)
    assert research_status == "pending"
    assert not RM.change_status(research_name, "nonexisting status")
    assert research_status == "pending"
    assert RM.change_status(research_name, "ongoing") == "ongoing"
    assert RM.status_of(research_name) == "ongoing"
    assert RM.count("all") == n_res + 1
    assert RM.count("pending") == n_res_pending
    assert RM.count("ongoing") == n_res_ongoing + 1

    # Research info
    research_info = RM.get_info(research_name)
    assert type(research_info) == dict
    assert research_info["research_id"] >= 1
    assert research_info["research_status"] == RM.status_of(research_name) == "ongoing"
    assert research_info["created_at"] < research_info["updated_at"]
    assert research_info["created_by"] == research_user_id
    assert research_info["n_samples"] == 0
    assert research_info["day_end"] == None
    assert research_info["research_comment"] == None
    assert RM.get_all()[research_name] == research_info
    assert len(RM.get_all()) == RM.count()
    assert RM.get_info(rstr()) == {}

    #changing other columns
    random_comment = rstr(100)
    bad_day_end = datetime.date(2019, 1, 1) # less than day_start
    good_day_end = datetime.date(2025, 1, 1)

    assert RM.change_comment(research_name, random_comment)
    assert not RM.change_day_end(research_name, bad_day_end)
    assert RM.change_day_end(research_name, good_day_end)

    research_updated_info = RM.get_info(research_name)
    assert research_updated_info["day_end"] == good_day_end
    assert research_updated_info["research_comment"] == random_comment

def kits():
    # Creating
    n_qrs = 10
    kit_id = KM.new(n_qrs)
    assert kit_id >= 1
    assert KM.has(kit_id)
    assert not KM.has(99999999)
    
    # Change status
    assert not KM.status_of(999999999)
    kit_status = KM.status_of(kit_id)
    assert KM.has_status(kit_status)
    assert kit_status == "created"
    assert not KM.change_status(kit_id, "rubbish")
    assert KM.change_status(kit_id, "sent") == "sent"
    
    # qrs
    assert len(set(KM.get_qrs(kit_id))) == n_qrs
    kit_new_id = KM.new(n_qrs)
    assert KM.has(kit_new_id)
    assert not KM.status_of(kit_new_id) == KM.status_of(kit_id)
    assert set(KM.get_qrs(kit_id)).intersection(set(KM.get_qrs(kit_new_id))) == set()

    # info
    kit_1_info = KM.get_info(kit_id)
    kit_2_info = KM.get_info(kit_new_id)
    assert KM.get_info(9999999) == {}
    assert isinstance(kit_1_info, dict) and isinstance(kit_2_info, dict)
    assert not kit_1_info == kit_2_info

    assert isinstance(kit_1_info["kit_unique_code"], bytes)
    assert not kit_1_info["kit_unique_code"] == kit_2_info["kit_unique_code"]
    assert kit_1_info["created_at"] < kit_1_info["updated_at"] < kit_2_info["created_at"] == kit_2_info["updated_at"]
    qr_key = list(kit_1_info["qrs"].keys())[3]
    assert isinstance(qr_key, int)
    qr_bytes = kit_1_info["qrs"][qr_key]
    assert isinstance(qr_bytes, bytes)
    assert KM.get_qr_info(qr_bytes)

    # Kit owners
    assert kit_1_info['owner'] == None
    owner_name = rstr()
    owner_id = UM.new(owner_name, rstr())
    assert not KM.change_owner(kit_id, rstr()) # wrong username
    assert KM.change_owner(kit_id, owner_name) == kit_id
    assert KM.get_info(kit_id)['owner'] == {'user_id': owner_id, 'username': owner_name}

def qrcodes():
    new_kit = KM.new(10)
    qrs = KM.get_qrs(new_kit)
    assert isinstance(qrs, dict)
    for id in qrs:
        binary = qrs[id]
        assert KM.get_qr_info(binary)
        assert not KM.get_qr_info(binary)['is_used']
        assert KM.get_qr_info(binary)['kit_id'] == new_kit


def samples():
    assert not SM.new(r'123141143', rstr(), datetime.datetime.now(), (2.4, 2.1))

    research_user = rstr()
    research_user_id = UM.new(research_user, rstr())
    assert UM.change_status(research_user, "admin")
    
    research_name = rstr()
    day_start = datetime.date(2020, 1, 1)
    research_id = RM.new(research_name, research_user, day_start)

    kit_id = KM.new(5)
    some_qr_bytes = list(KM.get_qrs(kit_id).values())[2]
    
    assert not SM.new(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # research is not ongoing
    RM.change_status(research_name, "ongoing")
    assert not SM.new(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # kit has no owner
    KM.change_owner(kit_id, research_user)
    assert not SM.new(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # kit has not been activated
    KM.change_status(kit_id, "activated")

    n_collected = UM.get_info(research_user)["n_samples_collected"]
    assert not KM.get_qr_info(some_qr_bytes)["is_used"]

    sample_id = SM.new(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # the PUSH
    assert isinstance(sample_id, int)
    assert UM.get_info(research_user)["n_samples_collected"] == n_collected + 1 == 1
    assert KM.get_qr_info(some_qr_bytes)["is_used"]
    assert not SM.new(some_qr_bytes, research_name, datetime.datetime.now(), (2.4, 2.1)) # QR is used


logdata = db_connection.DB_LOGDATA
logfile="test_strange.log"
UM = UsersManager(logdata, logfile=logfile)
KM = KitsManager(logdata, logfile=logfile)
RM = ResearchesManager(logdata, logfile=logfile)
SM = SamplesManager(logdata, logfile=logfile)
SM.clear_logs()
SM.logger.log_message("Info : Test started!")

rstr = lambda k=10: ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))
username_1 = rstr()
passwd_1 = rstr()
username_2 = rstr()
username_3 = rstr()
passwd_3 = rstr()

global test_time
test_time = time()
try:
    existing_statuses()
    new_user()
    user_info()
    user_renaming()
    counting_users()
    researches()
    kits()
    qrcodes()
    samples()
    print(f"All tests passed in {round(time()-test_time, ndigits=1)} s.")
except Exception as e:
    _, _, var = sys.exc_info()
    traceback.print_tb(var)
    tb_info = traceback.extract_tb(var)
    filename, line_number, _, text = tb_info[-1]
    SM.logger.log_message(f"An error occurred on line {line_number} in file {filename} in statement {text}")
    raise e
finally:
    SM.logger.log_message(f"Info : Test ended in {round(time()-test_time, ndigits=1)} s.")