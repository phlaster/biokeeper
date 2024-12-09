import random
import string
import sys
import traceback
import datetime
from time import time
from json import dumps

import sys
sys.path.append('python/src')
from DBManager import DBManager, LOGDATA

rstr = lambda k=10: ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))

def existing_statuses(DBM):
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
    assert DBM.researches.has_status('canceled')
    assert not DBM.researches.has_status("wrongstatus")

    assert DBM.samples.has_status("collected")
    assert DBM.samples.has_status("sent")
    assert DBM.samples.has_status("delivered")
    assert not DBM.samples.has_status("wrongstatus")
    print("Done: existing_statuses")

def new_user(DBM):
    username = rstr()
    
    assert not DBM.users.has(username, log=True)
    n_users = DBM.users.count("all")
    n_admins = DBM.users.count("admin")
    n_volunteers = DBM.users.count("volunteer")
    n_observers = DBM.users.count("observer")
    assert DBM.users.count() == n_users == n_admins + n_volunteers + n_observers

    # Counting
    user_1_id = DBM.users.new(username, rstr(), log=True)
    assert isinstance(user_1_id, int)
    assert DBM.users.has(username, log=True)
    assert DBM.users.count() == n_users + 1
    assert DBM.users.count("observer") == n_observers + 1

    # Status checks
    assert DBM.users.status_of(username, log=True) == "observer"
    assert not DBM.users.change_status(username, "wrongstatus", log=True)
    assert DBM.users.count("observer") == n_observers + 1
    assert DBM.users.change_status(username, "admin", log=True) == "admin"
    assert DBM.users.count("observer") == n_observers
    assert DBM.users.count("admin") == n_admins + 1
    assert DBM.users.status_of(username, log=True) == "admin"

    print("Done: new_user")
    
def user_password_validation(DBM):
    assert not DBM.users._validate_password("", "username")
    assert not DBM.users._validate_password("123", "username")
    assert DBM.users._validate_password("12345", "username")

    username = rstr()
    password = rstr()
    DBM.users.new(username, password, log=True)
    # Password match
    assert not DBM.users.password_match(username, rstr(), log=True)
    assert not DBM.users.password_match(username, "", log=True)
    assert not DBM.users.password_match(username, username, log=True)
    assert not DBM.users.password_match(password, password, log=True)
    assert DBM.users.password_match(username, password, log=True)

    # Password change
    new_password = rstr()
    assert DBM.users.change_user_password(username, new_password, log=True)
    assert not DBM.users.password_match(username, password, log=True)
    assert DBM.users.password_match(username, new_password, log=True)

    print("Done: user_password_validation")

def user_renaming(DBM):
    # Changing user_name
    user_name_1 = rstr()
    user_name_2 = rstr()
    passwd_1 = rstr()

    DBM.users.new(user_name_1, passwd_1, log=True)
    user_1_info = DBM.users.get_info(user_name_1)

    assert DBM.users.rename(user_name_1, user_name_2, log=True) == user_name_2
    assert not DBM.users.has(user_name_1, log=True)
    assert DBM.users.has(user_name_2, log=True)

    user_2_info = DBM.users.get_info(user_name_2)
    # shared_items = {k: user_1_info[k] for k in user_1_info if k in user_2_info and user_1_info[k] == user_2_info[k]}
    # assert len(user_2_info) - len(shared_items) == 1
    assert user_1_info["updated_at"] <= user_2_info["updated_at"]


    # Password match after renaming
    assert DBM.users.password_match(user_name_2, passwd_1, log=True)
    assert not DBM.users.password_match(user_name_2, rstr(), log=True)


    # Password match after renaming
    assert DBM.users.password_match(user_name_2, passwd_1, log=True)
    assert not DBM.users.password_match(user_name_2, rstr(), log=True)

    print("Done: user_renaming")

def user_2_info(DBM):
    username = rstr()
    new_name = rstr()

    DBM.users.new(username, rstr(), log=True)
    DBM.users.change_status(username, 'volunteer', log=True)
    user_info = DBM.users.get_info(username)
    assert isinstance(user_info, dict)

    # assert user_info["created_at"] < user_info["updated_at"]
    assert user_info["n_samples_collected"] == 0
    assert user_info["status"] == DBM.users.status_of(username, log=True) == "volunteer"
    assert user_info["id"] >= 1
    assert DBM.users.get_all()[username] == user_info
    assert DBM.users.count() == len(DBM.users.get_all())
    assert DBM.users.get_info(rstr()) == {}

    print("Done: user_2_info")

def researches(DBM):
    research_user = rstr()
    research_user_id = DBM.users.new(research_user, rstr(), log=True)
    assert DBM.users.status_of(research_user, log=True) == "observer"
    
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
    assert not DBM.researches.new(research_name, research_user, day_start, log=True) # user has no privilege
    DBM.users.change_status(research_user, "admin", log=True)
    assert DBM.researches.new(research_name, research_user, day_start, log=True)
    assert DBM.researches.has(research_name, log=True)
    assert not DBM.researches.new(research_name, research_user, day_start, log=True) # same name collision
    assert DBM.researches.count("all") == n_res + 1
    assert DBM.researches.count("pending") == n_res_pending + 1
    assert DBM.researches.count("ongoing") == n_res_ongoing

    # Changing research status
    research_status = DBM.researches.status_of(research_name, log=True)
    assert research_status == "pending"
    assert not DBM.researches.change_status(research_name, "nonexisting status", log=True)
    assert research_status == "pending"
    assert DBM.researches.change_status(research_name, "ongoing", log=True) == "ongoing"
    assert DBM.researches.status_of(research_name, log=True) == "ongoing"
    assert DBM.researches.count("all") == n_res + 1
    assert DBM.researches.count("pending") == n_res_pending
    assert DBM.researches.count("ongoing") == n_res_ongoing + 1

    # Research info
    research_info = DBM.researches.get_info(research_name)
    assert type(research_info) == dict
    assert research_info["id"] >= 1
    assert research_info["status"] == DBM.researches.status_of(research_name, log=True) == "ongoing"
    assert research_info["created_at"] <= research_info["updated_at"]
    assert research_info["created_by"] == research_user_id
    assert research_info["n_samples"] == 0
    assert research_info["day_end"] == None
    assert research_info["comment"] == None
    assert DBM.researches.get_all()[research_info["id"]] == research_info
    assert len(DBM.researches.get_all()) == DBM.researches.count()
    assert DBM.researches.get_info(rstr()) == {}

    #changing other columns
    random_comment = rstr(100)
    bad_day_end = datetime.date(2019, 1, 1) # less than day_start
    good_day_end = datetime.date(2025, 1, 1)

    assert DBM.researches.change_comment(research_name, random_comment, log=True)
    assert not DBM.researches.change_day_end(research_name, bad_day_end, log=True)
    assert DBM.researches.change_day_end(research_name, good_day_end, log=True)

    research_updated_info = DBM.researches.get_info(research_name)
    assert research_updated_info["day_end"] == good_day_end.isoformat()
    assert research_updated_info["comment"] == random_comment

    print("Done: researches")

def kits(DBM):
    # Creating
    n_qrs = 10
    kit_id = DBM.kits.new(n_qrs, log=True)
    assert kit_id >= 1
    assert DBM.kits.has(kit_id, log=True)
    assert not DBM.kits.has(99999999, log=True)
    
    # Change status
    assert not DBM.kits.status_of(999999999, log=True)
    kit_status = DBM.kits.status_of(kit_id, log=True)
    assert DBM.kits.has_status(kit_status)
    assert kit_status == "created"
    assert not DBM.kits.change_status(kit_id, "rubbish", log=True)
    assert not DBM.kits.change_status(-1, "rubbish", log=True)
    assert DBM.kits.change_status(kit_id, "sent", log=True) == "sent"
    
    # qrs
    assert len(set(DBM.kits.get_qrs(kit_id))) == n_qrs
    kit_new_id = DBM.kits.new(n_qrs, log=True)
    assert DBM.kits.has(kit_new_id, log=True)
    assert not DBM.kits.status_of(kit_new_id) == DBM.kits.status_of(kit_id, log=True)
    assert set(DBM.kits.get_qrs(kit_id, log=True)).intersection(set(DBM.kits.get_qrs(kit_new_id))) == set()

    # info
    kit_1_info = DBM.kits.get_info(kit_id)
    kit_2_info = DBM.kits.get_info(kit_new_id)
    assert DBM.kits.get_info(9999999) == {}
    assert isinstance(kit_1_info, dict) and isinstance(kit_2_info, dict)
    assert not kit_1_info == kit_2_info

    assert isinstance(kit_1_info["unique_hex"], str)
    assert not kit_1_info["unique_hex"] == kit_2_info["unique_hex"]
    assert kit_1_info["created_at"] <= kit_1_info["updated_at"] <= kit_2_info["created_at"] <= kit_2_info["updated_at"]
    qr_key = list(kit_1_info["qrs"].keys())[3]
    assert isinstance(qr_key, int)
    qr_hex = kit_1_info["qrs"][qr_key]
    assert isinstance(qr_hex, str)
    assert DBM.kits.get_qr_info(qr_hex)

    # Kit owners
    assert kit_1_info['owner'] == None
    owner_name = rstr()
    owner_id = DBM.users.new(owner_name, rstr(), log=True)
    assert not DBM.kits.change_owner(kit_id, rstr()) # wrong user_name
    assert DBM.kits.change_owner(kit_id, owner_name) == kit_id
    assert DBM.kits.get_info(kit_id)['owner'] == {'id': owner_id, 'name': owner_name}

    print("Done: kits")

def qrcodes(DBM):
    new_kit = DBM.kits.new(10, log=True)
    qrs = DBM.kits.get_qrs(new_kit, log=True)
    assert isinstance(qrs, dict)
    for id in qrs:
        hexcode = qrs[id]
        assert DBM.kits.get_qr_info(hexcode)
        assert not DBM.kits.get_qr_info(hexcode)['is_used']
        assert DBM.kits.get_qr_info(hexcode)['kit_id'] == new_kit

    print("Done: qrcodes")

def samples(DBM):
    assert not DBM.samples.new("589461abcbfc6451a586", rstr(), datetime.datetime.now(datetime.timezone.utc), (2.4, 2.1), log=True)

    research_user = rstr()
    research_user_id = DBM.users.new(research_user, rstr(), log=True)
    assert DBM.users.change_status(research_user, "admin", log=True)
    
    research_name = rstr()
    day_start = datetime.date(2020, 1, 1)
    research_id = DBM.researches.new(research_name, research_user, day_start, log=True)

    kit_id = DBM.kits.new(5, log=True)
    some_qr_bytes = list(DBM.kits.get_qrs(kit_id).values())[2]

    assert not DBM.samples.new(some_qr_bytes, research_name, datetime.datetime.now(datetime.timezone.utc), (2.4, 2.1), log=True) # research is not ongoing
    DBM.researches.change_status(research_name, "ongoing", log=True)
    assert not DBM.samples.new(some_qr_bytes, research_name, datetime.datetime.now(datetime.timezone.utc), (2.4, 2.1), log=True) # kit has no owner
    DBM.kits.change_owner(kit_id, research_user)
    assert not DBM.samples.new(some_qr_bytes, research_name, datetime.datetime.now(datetime.timezone.utc), (2.4, 2.1), log=True) # kit has not been activated
    DBM.kits.change_status(kit_id, "activated", log=True)

    n_collected = DBM.users.get_info(research_user)["n_samples_collected"]
    assert not DBM.kits.get_qr_info(some_qr_bytes)["is_used"]

    n_samples = DBM.samples.count()
    n_samples_collected = DBM.samples.count("collected")
    n_samples_sent = DBM.samples.count("sent")
    n_samples_delivered = DBM.samples.count("delivered")
    assert n_samples == DBM.samples.count("all")
    assert n_samples_delivered + n_samples_sent + n_samples_collected == n_samples

    assert not DBM.samples.new(some_qr_bytes, research_name, datetime.datetime.now(datetime.timezone.utc), (-95.9, 181.9), log=True) # incorrect coordinates
    sample_id = DBM.samples.new(some_qr_bytes, research_name, datetime.datetime.now(datetime.timezone.utc), (2.4, 2.1), log=True) # the PUSH
    assert isinstance(sample_id, int)
    assert DBM.users.get_info(research_user)["n_samples_collected"] == n_collected + 1 == 1
    assert DBM.kits.get_qr_info(some_qr_bytes)["is_used"]
    assert not DBM.samples.new(some_qr_bytes, research_name, datetime.datetime.now(datetime.timezone.utc), (2.4, 2.1), log=True) # QR is used

    assert n_samples + 1 == DBM.samples.count("all")
    assert DBM.samples.count("collected") == n_samples_collected + 1

    assert DBM.samples.has(sample_id, log=True)
    assert not DBM.samples.has(sample_id+1, log=True)

    assert DBM.samples.has_status("collected")
    assert DBM.samples.has_status("sent")
    assert DBM.samples.has_status("delivered")
    assert not DBM.samples.has_status("lost")

    assert DBM.samples.status_of(sample_id, log=True) == "collected"
    assert not DBM.samples.change_status(sample_id, "rubbish", log=True)
    assert DBM.samples.status_of(sample_id, log=True) == "collected"
    assert DBM.samples.change_status(sample_id, "sent", log=True)
    assert DBM.samples.status_of(sample_id, log=True) == "sent"
    assert DBM.samples.count("sent") == n_samples_sent + 1
    assert n_samples + 1 == DBM.samples.count("all")

    print("Done: samples")

def dispatch_testing(DBM):
    username = rstr()
    passwd = rstr()
    user_id = DBM.users.new(username, passwd, log=True)

    assert user_id == DBM.users.has(username, log=True) == DBM.users.has(user_id, log=True)
    assert DBM.users.password_match(username, passwd, log=True)
    assert DBM.users.password_match(user_id, passwd, log=True)
    assert DBM.users.get_info(user_id) == DBM.users.get_info(username)

    print("Done: dispatch_testing")

def gte(DBM):
    example = DBM.generate_test_example(log=True)
    with open("dump.json", "w") as f:
        f.write(dumps(example))
    sample_id = example["sample"]["id"]

    print("Done: gte")


def main():
    logfile="DBManager_tests.log"
    DBM = DBManager(LOGDATA, logfile)
    DBM.logger.clear_logs()
    DBM.logger.log("Info : Test started!")
    test_time = time()

    try:
        existing_statuses(DBM)
        new_user(DBM)
        user_password_validation(DBM)
        user_2_info(DBM)
        user_renaming(DBM)
        researches(DBM)
        kits(DBM)
        qrcodes(DBM)
        samples(DBM)
        dispatch_testing(DBM)
        gte(DBM)
        print(f"All tests passed in {round(time()-test_time, ndigits=1)} s.")
    except Exception as e:
        _, _, var = sys.exc_info()
        traceback.print_tb(var)
        tb_info = traceback.extract_tb(var)
        filename, line_number, _, text = tb_info[-1]
        DBM.logger.log(f"An error occurred on line {line_number} in file {filename} in statement {text}")
        raise e
    finally:
        DBM.logger.log(f"Info : Test ended in {round(time()-test_time, ndigits=1)} s.")

if __name__ == "__main__":
    main()