from DBConnection import DBConnection
from Logger import Logger
import hashlib
import os
import re
import datetime

class DBManager:
    def __init__(self, logdata, logfile="logs.log"):
        self.logdata = logdata
        self.logger = Logger(logfile)

    def _clear_logs(self):
        self.logger.clear_logs()
    
    def _generate_qr_bytes(self, n: int, l: int):
        return [os.urandom(l) for _ in range(n)]
    ################# Validations #################
    def _validate_password(self, password:str, username: str):
        """
        --- logging ---

        Simplest validation possible. Rest is for the frontenders
        """
        if len(password) > 4:
            return True
        else:
            self.logger.log_message(f"Error: Password validation for '{username}' failed.")
            return False
    def _validate_username(self, username:str):
        """
        --- logging ---
        Simplest validations for a username
        """
        if len(username) > 4:
            return True
        else:
            self.logger.log_message(f"Error: Username '{username}' validation failed.")
            return False

    
    ################# Pasword hashing #################
    def _hashing(self, password_bytes: bytes, salt: bytes) -> bytes:
        """
        hashing password with salt
        """
        return hashlib.scrypt(password_bytes, salt=salt, n=2**14, r=8, p=1)
    def _hash_and_salt(self, password: str) -> tuple[bytes, bytes]:
        """
        Hashes a password with a salt using the scrypt algorithm.
        """
        salt = os.urandom(16)
        password_bytes = password.encode('utf-8')
        hashed = self._hashing(password_bytes, salt)
        return (hashed, salt)

    
    ################# Counting #################
    def n_users(self, status:str="all"):
        """
        Returns number of users with different statuses.
        'all' for all statuses OR
        Currently possible statuses: "admin", "volunteer", "observer"
        """
        with DBConnection(self.logdata) as (conn, cursor):
            if status == "all":
                cursor.execute("SELECT COUNT(*) FROM users")
            else:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM users 
                    WHERE user_status IN (
                        SELECT status_id 
                        FROM user_statuses 
                        WHERE status_key = %s
                    )
                """, (status,))
            result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0
    def n_researches(self, status:str="all"):
        """
        Returns number of researches with different statuses.
        'all' for all statuses OR
        Currently possible statuses: "pending", "ongoing", "paused", "ended", "cancelled"
        """
        with DBConnection(self.logdata) as (conn, cursor):
            if status == "all":
                cursor.execute("SELECT COUNT(*) FROM researches")
            else:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM researches 
                    WHERE research_status IN (
                        SELECT status_id 
                        FROM research_statuses 
                        WHERE status_key = %s
                    )
                """, (status,))
            result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0
    def n_kits(self, status:str="all"):
        """
        Returns number of kits with different statuses.
        'all' for all statuses OR
        Currently possible statuses: "created", "sent", "activated"
        """
        with DBConnection(self.logdata) as (conn, cursor):
            if status == "all":
                cursor.execute("SELECT COUNT(*) FROM kits")
            else:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM kits 
                    WHERE kit_status IN (
                        SELECT status_id 
                        FROM kit_statuses 
                        WHERE status_key = %s
                    )
                """, (status,))
            result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

    
    ################# True/False #################
    def is_status_of(self, table_prefix: str, status: str):
        """
        -- logging --
        returns (status_id, status_info) if successfull;
        Examples:
        is_status_of("user", "admin") == True
        is_status_of("kit", "thrown away") == False     # kit has no status 'thrown away'
        """
        with DBConnection(self.logdata) as (conn, cursor):
            table_name = f"{table_prefix}_statuses"
            try:
                cursor.execute(f"""
                    SELECT status_id, status_info
                    FROM {table_name}
                    WHERE status_key = '{status}'
                """)
                result = cursor.fetchone()
            except Exception as e:
                self.logger.log_message(f"Error: {e}".split("\n")[0])
                return False
        if result:
            return result
        else:
            return False
    def is_password_match(self, username: str, password: str):
        """
        -- logging --
        """
        if not self.is_user(username):
            self.logger.log_message(f"Error: Authentication attempt for nonexisting username '{username}'.")
            return False

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT password_hash, password_salt FROM users WHERE username = %s", (username,))
            stored_hash, stored_salt = cursor.fetchone()
        rehashed_password = self._hashing(password.encode('utf-8'), stored_salt)

        return rehashed_password == bytes(stored_hash)
    
    def is_user(self, username: str):
        """
        returns user_id if successfull
        """
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
        return result[0] if result is not None else False
    def is_research(self, research_name: str):
        """
        returns research_id if successfull
        """
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT research_id FROM researches WHERE research_name = %s", (research_name,))
            result = cursor.fetchone()
        return result[0] if result is not None else False
    def is_kit(self, kit_id: str):
        """
        returns kit_id if successfull
        """
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT kit_id FROM kits WHERE kit_id = %s", (kit_id,))
            result = cursor.fetchone()
        return result[0] if result is not None else False

    
    ################# Selections #################
    def get_user_status(self, username: str):
        """
        -- logging --
        if username is incorrect returns False
        """
        if not self.is_user(username):
            self.logger.log_message(f"Error: Attempt to check status of an nonexisting user '{username}'.")
            return False
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT user_status FROM users WHERE username = %s", (username,))
            user_status_id = cursor.fetchone()
            cursor.execute("SELECT status_key FROM user_statuses WHERE status_id = %s", (user_status_id,))
            status_key = cursor.fetchone()[0]
        return status_key
    def get_user_info(self, username: str):
        """
        Returns user information as a dictionary for the given username.
        If the user does not exist, an empty dictionary is returned (equivalent to False).
        """
        user_info_dict = {}

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("""
                SELECT user_id, user_status, created_at, updated_at, n_samples_collected
                FROM users
                WHERE username = %s
            """, (username,))
            user_data = cursor.fetchone()

            if user_data:
                user_info_dict['user_id'] = user_data[0]

                # Fetching status_key from user_statuses table
                cursor.execute("SELECT status_key FROM user_statuses WHERE status_id = %s", (user_data[1],))
                status_key = cursor.fetchone()[0]
                user_info_dict['user_status'] = status_key

                user_info_dict['created_at'] = user_data[2]
                user_info_dict['updated_at'] = user_data[3]
                user_info_dict['n_samples_collected'] = user_data[4]
        return user_info_dict
    def get_all_users(self):
        """
        Returns a dictionary where the keys are usernames and the values are
        the corresponding user information dictionaries.
        """
        all_users_dict = {}

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT username FROM users")
            usernames = cursor.fetchall()

        for username_tuple in usernames:
            username = username_tuple[0]
            user_info_dict = self.get_user_info(username)
            all_users_dict[username] = user_info_dict

        return all_users_dict
    
    def get_research_status(self, research_name: str):
        """
        Returns the status key of the research with the given name.
        If the research does not exist, False is returned.
        """
        if not self.is_research(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' does not exist.")
            return False

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("""
                SELECT research_status
                FROM researches
                WHERE research_name = %s
            """, (research_name,))
            research_status_id = cursor.fetchone()[0]

            cursor.execute("""
                SELECT status_key
                FROM research_statuses
                WHERE status_id = %s
            """, (research_status_id,))
            status_key = cursor.fetchone()[0]

        return status_key
    def get_research_info(self, research_name: str):
        """
        Returns research information as a dictionary for the given research name.
        If the research does not exist, an empty dictionary is returned (equivalent to False).
        """
        research_info_dict = {}
        if not self.is_research(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' does not exist.")
            return research_info_dict

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("""
                SELECT research_id, research_status, created_at, updated_at, created_by, day_start, day_end, n_samples, research_comment
                FROM researches
                WHERE research_name = %s
            """, (research_name,))
            research_data = cursor.fetchone()

            if research_data:
                research_info_dict['research_id'] = research_data[0]

                cursor.execute("SELECT status_key FROM research_statuses WHERE status_id = %s", (research_data[1],))
                status_key = cursor.fetchone()[0]
                research_info_dict['research_status'] = status_key

                research_info_dict['created_at'] = research_data[2]
                research_info_dict['updated_at'] = research_data[3]
                research_info_dict['created_by'] = research_data[4]
                research_info_dict['day_start'] = research_data[5]
                research_info_dict['day_end'] = research_data[6]
                research_info_dict['n_samples'] = research_data[7]
                research_info_dict['research_comment'] = research_data[8]

        return research_info_dict
    def get_all_researches(self):
        """
        Returns a dictionary where the keys are research names and the values are
        the corresponding research information dictionaries.
        """
        all_researches_dict = {}

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT research_name FROM researches")
            research_names = cursor.fetchall()

        for research_name in research_names:
            research_info_dict = self.get_research_info(research_name[0])
            all_researches_dict[research_name[0]] = research_info_dict

        return all_researches_dict 

    def get_kit_status(self, kit_id: int):
        """
        -- logging --
        Returns the status of a kit with the given kit_id.
        If the kit does not exist, returns False.
        """
        if not self.is_kit(kit_id):
            self.logger.log_message(f"Error: Kit with ID {kit_id} does not exist.")
            return False

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT kit_status FROM kits WHERE kit_id = %s", (kit_id,))
            kit_status_id = cursor.fetchone()[0]

            cursor.execute("SELECT status_key FROM kit_statuses WHERE status_id = %s", (kit_status_id,))
            kit_status = cursor.fetchone()[0]

        return kit_status
    def get_kit_qrs(self, kit_id: int):
        """
        -- logging --
        Returns a list of tuples containing (qr_id, qr_unique_code) for the kit with the given kit_id.
        If the kit does not exist, returns empty dict.
        """
        qr_info = {}
        if not self.is_kit(kit_id):
            self.logger.log_message(f"Error: Kit with ID {kit_id} does not exist.")
            return qr_info


        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT qr_id, qr_unique_code FROM qrs WHERE kit_id = %s", (kit_id,))
            qr_info_tuples = cursor.fetchall()

        for qr_id, qr_unique_code in qr_info_tuples:
            qr_info[qr_id] = bytes(qr_unique_code)

        return qr_info
    def get_kit_info(self, kit_id: int):
        """
        -- logging --
        Returns a dictionary containing kit information for the kit with the given kit_id.
        If the kit does not exist, returns empty dict.
        """
        kit_info_dict = {}
        if not self.is_kit(kit_id):
            self.logger.log_message(f"Error: Kit with ID {kit_id} does not exist.")
            return kit_info_dict

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT kit_unique_code, created_at, updated_at, kit_status, user_id FROM kits WHERE kit_id = %s", (kit_id,))
            kit_data = cursor.fetchone()

            if kit_data:
                kit_info_dict['kit_unique_code'] = bytes(kit_data[0])
                kit_info_dict['created_at'] = kit_data[1]
                kit_info_dict['updated_at'] = kit_data[2]

                cursor.execute("SELECT status_key FROM kit_statuses WHERE status_id = %s", (kit_data[3],))
                kit_status_key = cursor.fetchone()[0]
                kit_info_dict['kit_status'] = kit_status_key

                if kit_data[4]:  # Check if user_id is not None
                    cursor.execute("SELECT user_id, username FROM users WHERE user_id = %s", (kit_data[4],))
                    owner_data = cursor.fetchone()
                    owner_dict = {'user_id': owner_data[0], 'username': owner_data[1]} if owner_data else None
                    kit_info_dict['owner'] = owner_dict
                else:
                    kit_info_dict['owner'] = None

                kit_info_dict['qrs'] = self.get_kit_qrs(kit_id)

        return kit_info_dict
    def get_all_kits(self):
        """
        Returns a dictionary where keys are kit_id and values are the result of get_kit_info call for each kit.
        """
        all_kits_dict = {}

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT kit_id FROM kits")
            kit_ids = cursor.fetchall()

        for kit_id_tuple in kit_ids:
            kit_id = kit_id_tuple[0]
            kit_info = self.get_kit_info(kit_id)
            all_kits_dict[kit_id] = kit_info

        return all_kits_dict

    def get_qr_info(self, qr_bytes: bytes):
        """
        returns dict with QR info if successfull
        empty dict otherwise
        """
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT qr_id, is_used, kit_id FROM qrs WHERE qr_unique_code = %s", (qr_bytes,))
            result = cursor.fetchone()

        if result:
            return {'qr_id': int(result[0]), 'is_used': bool(result[1]), 'kit_id': int(result[2])}
        else:
            return {}


    ################# Insertions #################
    def new_user(self, username:str, password:str):
        """
        -- logging --
        Returns the user_id if successful, otherwise False.
        """
        if self.is_user(username):
            self.logger.log_message(f"Error: Username '{username}' is already taken.")
            return False
        if not self._validate_username(username):
            return False
        if not self._validate_password(password, username):
            return False
        
        password_hash, salt = self._hash_and_salt(password)

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("""
                INSERT INTO users (username, password_hash, password_salt)
                VALUES (%s, %s, %s)
                RETURNING user_id
            """, (username, password_hash, salt))
            user_id = cursor.fetchone()[0]
            conn.commit()
        self.logger.log_message(f"Info : User #{user_id} '{username}' has been created")
        return user_id 
    def new_research(self, research_name: str, username: str, day_start: datetime.date, research_comment: str = None):
        """
        -- logging --
        Returns the research_id if successful, otherwise False.
        """
        if self.is_research(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' is already exists.")
            return False
        user_id = self.is_user(username)
        if not user_id:
            self.logger.log_message(f"Error: Can't assign new research '{research_name}' to a nonexisting user '{username}'.")
            return False

        user_status = self.get_user_status(username)
        if user_status != "admin":
            self.logger.log_message(f"Error: User '{username}' of status '{user_status}' has no privilege to create researches.")
            return False

        with DBConnection(self.logdata) as (conn, cursor):
            # Insert new research
            cursor.execute("""
                INSERT INTO researches (research_name, research_comment, created_by, day_start)
                VALUES (%s, %s, %s, %s)
                RETURNING research_id
            """, (research_name, research_comment, user_id, day_start))
            research_id = cursor.fetchone()[0]
            conn.commit()
        self.logger.log_message(f"Info : Research #{research_id} '{research_name}' starting on {day_start} created by '{username}'")
        return research_id
    def new_kit(self, n_qrs: int):
        """
        -- logging --
        Inserts a new kit with `n_qrs` QRs into the database.
        Returns the kit_id if successful, otherwise False.
        """
        kit_unique_code = os.urandom(16)
        qr_unique_codes = self._generate_qr_bytes(n_qrs, 10)
        
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("""
                INSERT INTO kits (kit_unique_code, n_qrs)
                VALUES (%s, %s)
                RETURNING kit_id
            """, (kit_unique_code, n_qrs))
            kit_id = cursor.fetchone()[0]

            for qr_unique_code in qr_unique_codes:
                cursor.execute("""
                    INSERT INTO qrs (qr_unique_code, kit_id)
                    VALUES (%s, %s)
                """, (qr_unique_code, kit_id))
            conn.commit()
        self.logger.log_message(f"Info : Kit #{kit_id} with {n_qrs} QRs has been created")
        return kit_id

    def new_sample(self,
        qr_bytes: bytes,
        research_name: str,
        collected_at: datetime.datetime,
        gps: tuple[float, float],
        weather: str = None,
        user_comment: str = None,
        photo: bytes = None
    ):
        """
        -- logging --
        Returns sample_id if successfull
        Inserts a new sample into the database with the provided information.
        Checks if the research is ongoing, the QR code is valid and not used, the kit is activated, and the user is a volunteer.
        Increments the n_samples_collected of the user by 1 if all conditions are met.
        """
        if collected_at > datetime.datetime.now():
            self.logger.log_message(f"Warn : The sample seems to be collected in future at {collected_at}.")

        research_info = self.get_research_info(research_name)
        if not research_info:
            self.logger.log_message(f"Error: Invalid research name '{research_name}'.")
            return False

        if research_info["research_status"] != "ongoing":
            self.logger.log_message(f"Error: Research '{research_name}' is not in 'ongoing' status.")
            return False

        qr_info = self.get_qr_info(qr_bytes)
        if not qr_info:
            self.logger.log_message(f"Error: No such QR in database.")
            return False
        
        qr_id = qr_info["qr_id"]
        if qr_info["is_used"]:
            self.logger.log_message(f"Error: QR #{qr_id} already 'is_used'.")
            return False
        
        kit_id = qr_info["kit_id"]
        if not kit_id:
            self.logger.log_message(f"Error: QR code is not assigned to any kit.")
            return False

        kit_info = self.get_kit_info(kit_id)
        if not kit_info:
            self.logger.log_message(f"Error: No #{kit_id} was found (very strange!).")
            return False
        
        kit_owner = kit_info["owner"]
        if not kit_owner:
            self.logger.log_message(f"Error: Kit #{kit_id} has no owner.")
            return False

        if kit_info["kit_status"] != "activated":
            self.logger.log_message(f"Error: Kit associated with QR hasn't been activated.")
            return False

        kit_owner_status = self.get_user_status(kit_owner["username"])
        if kit_owner_status not in ['admin', 'volunteer']:
            self.logger.log_message(f"Error: Owner of kit '{kit_owner}' is of status '{kit_owner_status}', which is not enough to publish samples.")
            return False
        
        with DBConnection(self.logdata) as (conn, cursor):

            cursor.execute("""
                INSERT INTO samples (research_id, qr_id, collected_at, gps, weather_conditions, user_comment, photo)
                VALUES (%s, %s, %s, POINT(%s), %s, %s, %s)
                RETURNING sample_id
            """, (research_info['research_id'], qr_id, collected_at, str(gps), weather, user_comment, photo))
            sample_id = cursor.fetchone()[0]
            
            cursor.execute("UPDATE qrs SET is_used = true WHERE qr_id = %s", (qr_id,))
            self.logger.log_message(f"Info : QR #{qr_id} is now 'is_used'")
            cursor.execute("UPDATE users SET n_samples_collected = n_samples_collected + 1 WHERE user_id = %s RETURNING n_samples_collected", (kit_owner["user_id"],))
            new_personal_score = cursor.fetchone()[0]
            self.logger.log_message(f"Info : Personal counter of user '{kit_owner["username"]}' is now {new_personal_score}")
            conn.commit()

        self.logger.log_message("Info : New sample inserted successfully.")
        return sample_id


    ################# Updates #################
    def change_user_status(self, username: str, new_status: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.is_user(username):
            self.logger.log_message(f"Error: Can't change status of a nonexisting user '{username}'.")
            return False
        
        new_status_id = self.is_status_of("user", new_status)
        if not new_status_id:
            self.logger.log_message(f"Error: Status '{new_status}' is not a valid status.")
            return False

        if new_status == self.get_user_status(username):
            # No status change, no logging
            return new_status

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("UPDATE users SET user_status = %s WHERE username = %s", (new_status_id[0], username))
            conn.commit()
        self.logger.log_message(f"Info : User '{username}' changed status to '{new_status}'")
        return new_status
    def change_user_name(self, old_username: str, new_username: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.is_user(old_username):
            self.logger.log_message(f"Error: Can't change username of a nonexisting user '{old_username}'.")
            return False
        
        if old_username==new_username:
            # No username change, no logging
            return old_username

        if self.is_user(new_username):
            self.logger.log_message(f"Error: Can't change username '{old_username}' to '{new_username}' - the name is taken.")
            return False

        if not self._validate_username(new_username):
            return False
        
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("UPDATE users SET username = %s WHERE username = %s", (new_username, old_username))
            conn.commit()
            
        self.logger.log_message(f"Info : User '{old_username}' changed name to '{new_username}'.")
        return new_username
    def change_user_password(self, username: str, new_password: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.is_user(username):
            self.logger.log_message(f"Error: Can't change password of a nonexisting user '{username}'.")
            return False
        
        if not self._validate_password(new_password, username):
            return False
        
        with DBConnection(self.logdata) as (conn, cursor):
            hashed_password, salt = self._hash_and_salt(new_password)
            cursor.execute("""
                UPDATE users
                SET password_hash = %s, password_salt = %s
                WHERE username = %s;
            """, (hashed_password, salt, username))
            conn.commit()
        self.logger.log_message(f"Info : Changed password for user '{username}'.")
        return True

    def change_research_status(self, research_name: str, new_status: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.is_research(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' does not exist.")
            return False

        new_status_query = self.is_status_of("research", new_status)
        if not new_status_query:
            self.logger.log_message(f"Error: Status '{new_status}' is not a valid research status.")
            return False
        new_status_id = new_status_query[0]

        current_status = self.get_research_status(research_name)
        current_status_id = self.is_status_of("research", current_status)[0]

        if new_status_id == current_status_id:
            # No status change, no logging
            return new_status

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("UPDATE researches SET research_status = %s WHERE research_name = %s", (new_status_id, research_name))
            conn.commit()

        self.logger.log_message(f"Info : Research '{research_name}' status changed to '{new_status}'")
        return new_status
    def change_research_comment(self, research_name: str, comment: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.is_research(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' does not exist.")
            return False

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("UPDATE researches SET research_comment = %s WHERE research_name = %s", (comment, research_name))
            conn.commit()

        self.logger.log_message(f"Info : Updated comment for research '{research_name}'")
        return True
    def change_research_day_end(self, research_name: str, day_end: datetime.date):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.is_research(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' does not exist.")
            return False

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT day_start FROM researches WHERE research_name = %s", (research_name,))
            day_start = cursor.fetchone()[0]

            if day_end < day_start:
                self.logger.log_message(f"Error: Can't set ending day at {day_end} for research '{research_name}' that starts on {day_start}.")
                return False

            cursor.execute("UPDATE researches SET day_end = %s WHERE research_name = %s", (day_end, research_name))
            conn.commit()

        self.logger.log_message(f"Info : Now '{research_name}' ends on {day_end}")
        return True
    
    def change_kit_status(self, kit_id: int, new_status: str):
        """
        -- logging --
        Changes the status of a kit with the given kit_id to the new_status.
        Returns the new status if successful, otherwise False.
        """
        kit_id = str(kit_id)
        if not self.is_kit(kit_id):
            self.logger.log_message(f"Error: Kit #{kit_id} does not exist.")
            return False

        new_status_query = self.is_status_of("kit", new_status)
        if not new_status_query:
            self.logger.log_message(f"Error: Status '{new_status}' is not a valid kit status.")
            return False
        new_status_id = new_status_query[0]

        current_status = self.get_kit_status(kit_id)
        current_status_id = self.is_status_of("kit", current_status)[0]

        if new_status_id == current_status_id:
            # No status change, no logging
            return new_status

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("UPDATE kits SET kit_status = %s WHERE kit_id = %s", (new_status_id, kit_id))
            conn.commit()

        self.logger.log_message(f"Info : Kit #{kit_id} status changed to '{new_status}'")
        return new_status
    def change_kit_owner(self, kit_id: int, username: str):
        """
        -- logging --
        Changes the owner of a kit with the given kit_id to the user with the specified username.
        Returns kit_id if successful, otherwise False.
        """
        if not self.is_kit(kit_id):
            self.logger.log_message(f"Error: Kit with ID {kit_id} does not exist.")
            return False

        user_id = self.is_user(username)
        if not user_id:
            self.logger.log_message(f"Error: User '{username}' does not exist.")
            return False

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("UPDATE kits SET user_id = %s WHERE kit_id = %s", (user_id, kit_id))
            conn.commit()

        self.logger.log_message(f"Info : Owner of Kit #{kit_id} changed to '{username}'")
        return kit_id

    def change_sample_details(self, sample_id: int, weather: str = None, user_comment: str = None, photo: bytes = None):
        """
        -- logging --
        Updates the weather conditions, user comment, and photo of an existing sample in the database.
        Returns True if the update is successful, False otherwise.
        """
        if weather == user_comment == photo == None:
            return False
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT * FROM samples WHERE sample_id = %s", (sample_id,))
            sample_data = cursor.fetchone()
            if not sample_data:
                self.logger.log_message(f"Error: Sample #{sample_id} does not exist.")
                return False

            logmsg = []
            update_query = "UPDATE samples SET "
            update_values = []

            if weather is not None:
                update_query += "weather_conditions = %s, "
                update_values.append(weather)
                logmsg.append("weather info")

            if user_comment is not None:
                update_query += "user_comment = %s, "
                update_values.append(user_comment)
                logmsg.append("user comment")

            if photo is not None:
                update_query += "photo = %s, "
                update_values.append(photo)
                logmsg.append("photo")

            # Remove the trailing comma and space
            update_query = update_query[:-2]

            update_query += " WHERE sample_id = %s"
            update_values.append(sample_id)

            cursor.execute(update_query, update_values)
            conn.commit()
            self.logger.log_message(f"Info : Pushed details: {', '.join(logmsg)} for sample #{sample_id}.")
        return True
