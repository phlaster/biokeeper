from ADBM import AbstractDBManager
import hashlib
import os

class UsersManager(AbstractDBManager):
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



    def count(self, status = "all"):
        """
        Returns number of users with different statuses.
        'all' for all statuses OR
        Currently possible statuses: "admin", "volunteer", "observer"
        """
        return self._counter("users", "user_status", "user_statuses", status)

    def has_status(self, status):
        return self._is_status_of("user", status)

    def has(self, username):
        return self._is("user_id", "users", "username", username)

    def status_of(self, username: str):
        """
        -- logging --
        if username is incorrect returns False
        """
        if not self.has(username):
            self.logger.log_message(f"Error: Attempt to check status of an nonexisting user '{username}'.")
            return False
        return self._status_getter("user_status", "users", "username", "user_statuses", username)

    def get_info(self, username: str):
        """
        Returns user information as a dictionary for the given username.
        If the user does not exist, an empty dictionary is returned (equivalent to False).
        """
        user_info_dict = {}

        with self.db as (conn, cursor):
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

    def get_all(self):
        """
        Returns a dictionary where the keys are usernames and the values are
        the corresponding user information dictionaries.
        """
        all_users_dict = {}

        with self.db as (conn, cursor):
            cursor.execute("SELECT username FROM users")
            usernames = cursor.fetchall()

        for username_tuple in usernames:
            username = username_tuple[0]
            user_info_dict = self.get_info(username)
            all_users_dict[username] = user_info_dict

        return all_users_dict

    def new(self, username:str, password:str):
        """
        -- logging --
        Returns the user_id if successful, otherwise False.
        """
        if self.has(username):
            self.logger.log_message(f"Error: Username '{username}' is already taken.")
            return False
        if not self._validate_username(username):
            return False
        if not self._validate_password(password, username):
            return False
        
        password_hash, salt = self._hash_and_salt(password)

        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO users (username, password_hash, password_salt)
                VALUES (%s, %s, %s)
                RETURNING user_id
            """, (username, password_hash, salt))
            user_id = cursor.fetchone()[0]
            conn.commit()
        self.logger.log_message(f"Info : User #{user_id} '{username}' has been created")
        return user_id 

    def change_status(self, username: str, new_status: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.has(username):
            self.logger.log_message(f"Error: Can't change status of a nonexisting user '{username}'.")
            return False
        
        new_status_id = self.has_status(new_status)
        if not new_status_id:
            self.logger.log_message(f"Error: Status '{new_status}' is not a valid status.")
            return False

        if new_status == self.status_of(username):
            # No status change, no logging
            return new_status

        with self.db as (conn, cursor):
            cursor.execute("UPDATE users SET user_status = %s WHERE username = %s", (new_status_id[0], username))
            conn.commit()
        self.logger.log_message(f"Info : User '{username}' changed status to '{new_status}'")
        return new_status

    def change_name(self, old_username: str, new_username: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.has(old_username):
            self.logger.log_message(f"Error: Can't change username of a nonexisting user '{old_username}'.")
            return False
        
        if old_username==new_username:
            # No username change, no logging
            return old_username

        if self.has(new_username):
            self.logger.log_message(f"Error: Can't change username '{old_username}' to '{new_username}' - the name is taken.")
            return False

        if not self._validate_username(new_username):
            return False
        
        with self.db as (conn, cursor):
            cursor.execute("UPDATE users SET username = %s WHERE username = %s", (new_username, old_username))
            conn.commit()
            
        self.logger.log_message(f"Info : User '{old_username}' changed name to '{new_username}'.")
        return new_username

    def change_user_password(self, username: str, new_password: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.has(username):
            self.logger.log_message(f"Error: Can't change password of a nonexisting user '{username}'.")
            return False
        
        if not self._validate_password(new_password, username):
            return False
        
        with self.db as (conn, cursor):
            hashed_password, salt = self._hash_and_salt(new_password)
            cursor.execute("""
                UPDATE users
                SET password_hash = %s, password_salt = %s
                WHERE username = %s;
            """, (hashed_password, salt, username))
            conn.commit()
        self.logger.log_message(f"Info : Changed password for user '{username}'.")
        return True

    def password_match(self, username: str, password: str):
        """
        -- logging --
        """
        if not self.has(username):
            self.logger.log_message(f"Error: Authentication attempt for nonexisting username '{username}'.")
            return False

        with self.db as (conn, cursor):
            cursor.execute("SELECT password_hash, password_salt FROM users WHERE username = %s", (username,))
            stored_hash, stored_salt = cursor.fetchone()
        rehashed_password = self._hashing(password.encode('utf-8'), stored_salt)

        return rehashed_password == bytes(stored_hash)