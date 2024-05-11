import random
import string
import sys
from datetime import date, timedelta

sys.path.insert(1, './python/src')
import db_connection
from DBManager import DBManager

logdata = db_connection.DB_LOGDATA
db_manager = DBManager(logdata, logfile="test.log")
db_manager._clear_logs()
db_manager.logger.log_message("Test started!")

# Test username and password validation
assert db_manager._validate_username("validuser"), "Valid username should pass validation"
assert not db_manager._validate_username("a"), "Short username should fail validation"
assert db_manager._validate_password("validpassword", "name"), "Valid password should pass validation"
assert not db_manager._validate_password("a", "name"), "Short password should fail validation"

# Test new user creation
name_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
password_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
new_user_id = db_manager.new_user(name_1, password_1)
assert new_user_id, "new_user function failed to create a new user"

# Test existing user handling
existing_user_id = db_manager.new_user(name_1, password_1)
assert not existing_user_id, "new_user function failed to handle existing username conflict"

# Test user existence check
is_user = db_manager.is_user(name_1)
assert is_user, "is_user function failed to identify an existing user"
is_user = db_manager.is_user("invaliduser")
assert not is_user, "is_user function failed to handle nonexisting user"

# Test password matching
is_password_match = db_manager.is_password_match(name_1, password_1)
assert is_password_match, "is_password_match function failed to verify a correct password"
is_password_match = db_manager.is_password_match(name_1, "invalidpassword")
assert not is_password_match, "is_password_match function failed to handle incorrect password"

# Test user status retrieval
user_status = db_manager.get_user_status(name_1)
assert user_status == "observer", "user_status function returned an unexpected status"
user_status = db_manager.get_user_status("invaliduser")
assert not user_status, "user_status function failed to handle nonexisting user"

# Test user status change
new_status = db_manager.change_user_status(name_1, "volunteer")
assert new_status == "volunteer", "change_user_status function failed to update the user status"
new_status = db_manager.change_user_status(name_1, "invalidstatus")
assert not new_status, "change_user_status function failed to handle invalid new status"

# Test username change
name_2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
name_3 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
new_username = db_manager.change_user_name(name_1, name_2)
assert new_username == name_2, "change_user_name function failed to update the username"
new_username = db_manager.change_user_name(name_2, name_2)
assert new_username == name_2, "change_user_name function failed to handle no change in username"
db_manager.new_user(name_3, password_1)
new_username = db_manager.change_user_name(name_2, name_3)
assert not new_username, "change_user_name function failed to handle existing username conflict"

# Test password change
password_2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
password_changed = db_manager.change_user_password(name_2, password_2)
assert password_changed, "change_user_password function failed to update the password"
password_changed = db_manager.change_user_password("invaliduser", password_2)
assert not password_changed, "change_user_password function failed to handle invalid username"
password_changed = db_manager.change_user_password(name_2, "a")
assert not password_changed, "change_user_password function failed to handle invalid new password"

# Test user retrieval
all_users = db_manager.get_all_users()
assert name_3 in all_users, "all_users function failed to retrieve all users"

# Test user counting
n_users = db_manager.n_users()
assert n_users >= 2, "n_users function returned an unexpected number of users"
n_users_observer = db_manager.n_users("observer")
assert n_users_observer >= 1, "n_users function failed to count users by status"
n_users_volunteer = db_manager.n_users("volunteer")
assert n_users_volunteer >= 1, "n_users function failed to count users by status"

# Test change_user_status
def test_change_user_status():
    name_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    password_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    new_user_id = db_manager.new_user(name_1, password_1)
    assert new_user_id, "new_user function failed to create a new user"

    new_status = db_manager.change_user_status(name_1, "volunteer")
    assert new_status == "volunteer", "change_user_status function failed to update the user status"

    new_status = db_manager.change_user_status(name_1, "invalidstatus")
    assert not new_status, "change_user_status function failed to handle invalid new status"

    new_status = db_manager.change_user_status("invaliduser", "volunteer")
    assert not new_status, "change_user_status function failed to handle non-existent user"

# Test change_user_name
def test_change_user_name():
    name_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    password_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    new_user_id = db_manager.new_user(name_1, password_1)
    assert new_user_id, "new_user function failed to create a new user"

    name_2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    new_username = db_manager.change_user_name(name_1, name_2)
    assert new_username == name_2, "change_user_name function failed to update the username"

    new_username = db_manager.change_user_name(name_2, name_2)
    assert new_username == name_2, "change_user_name function failed to handle no change in username"

    name_3 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    db_manager.new_user(name_3, password_1)
    new_username = db_manager.change_user_name(name_2, name_3)
    assert not new_username, "change_user_name function failed to handle existing username conflict"

    new_username = db_manager.change_user_name("invaliduser", name_2)
    assert not new_username, "change_user_name function failed to handle non-existent user"

    new_username = db_manager.change_user_name(name_2, "a")
    assert not new_username, "change_user_name function failed to handle invalid new username"

# Test change_user_password
def test_change_user_password():
    name_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    password_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    new_user_id = db_manager.new_user(name_1, password_1)
    assert new_user_id, "new_user function failed to create a new user"

    password_2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    password_changed = db_manager.change_user_password(name_1, password_2)
    assert password_changed, "change_user_password function failed to update the password"

    password_changed = db_manager.change_user_password("invaliduser", password_2)
    assert not password_changed, "change_user_password function failed to handle non-existent user"

    password_changed = db_manager.change_user_password(name_1, "a")
    assert not password_changed, "change_user_password function failed to handle invalid new password"

# Test change_research_status
def test_change_research_status():
    name_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    password_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    new_user_id = db_manager.new_user(name_1, password_1)
    assert new_user_id, "new_user function failed to create a new user"

    research_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    research_comment = "Test research"
    day_start = date.today()
    new_research_id = db_manager.new_research(research_name, research_comment, name_1, day_start)
    assert not new_research_id, "unpriveledged user created the research!"

    db_manager.change_user_status(name_1, "admin")
    new_research_id = db_manager.new_research(research_name, research_comment, name_1, day_start)
    assert new_research_id, "could not create research!"

    new_status = db_manager.change_research_status(research_name, "ongoing")
    assert new_status == "ongoing", "change_research_status function failed to update the research status"

    new_status = db_manager.change_research_status(research_name, "invalidstatus")
    assert not new_status, "change_research_status function failed to handle invalid new status"

    new_status = db_manager.change_research_status("invalidresearch", "ongoing")
    assert not new_status, "change_research_status function failed to handle non-existent research"

# Test change_research_comment
def test_change_research_comment():
    name_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    password_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    new_user_id = db_manager.new_user(name_1, password_1)
    assert new_user_id, "new_user function failed to create a new user"

    research_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    research_comment = "Test research"
    day_start = date.today()
    db_manager.change_user_status(name_1, "admin")
    new_research_id = db_manager.new_research(research_name, research_comment, name_1, day_start)
    assert new_research_id, "could not create research!"

    new_comment = "Updated research comment"
    comment_changed = db_manager.change_research_comment(research_name, new_comment)
    assert comment_changed, "change_research_comment function failed to update the research comment"

    comment_changed = db_manager.change_research_comment("invalidresearch", new_comment)
    assert not comment_changed, "change_research_comment function failed to handle non-existent research"

# Test change_research_day_end
def test_change_research_day_end():
    name_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    password_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    new_user_id = db_manager.new_user(name_1, password_1)
    assert new_user_id, "new_user function failed to create a new user"

    research_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    research_comment = "Test research"
    day_start = date.today()
    db_manager.change_user_status(name_1, "admin")
    new_research_id = db_manager.new_research(research_name, research_comment, name_1, day_start)
    assert new_research_id, "could not create research!"

    day_end = day_start + timedelta(days=7)
    day_end_changed = db_manager.change_research_day_end(research_name, day_end)
    assert day_end_changed, "change_research_day_end function failed to update the research end date"

    day_end = day_start - timedelta(days=7)
    day_end_changed = db_manager.change_research_day_end(research_name, day_end)
    assert not day_end_changed, "change_research_day_end function failed to handle end date before start date"

    day_end_changed = db_manager.change_research_day_end("invalidresearch", day_end)
    assert not day_end_changed, "change_research_day_end function failed to handle non-existent research"

test_change_user_status()
test_change_user_name()
test_change_user_password()
test_change_research_status()
test_change_research_comment()
test_change_research_day_end()

print("All tests passed!")
