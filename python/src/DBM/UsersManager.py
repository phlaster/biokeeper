from ADBM import AbstractDBManager
import hashlib
import os

class UsersManager(AbstractDBManager):
    def _validate_password(self, password:str, user_name: str):
        """
        --- logging ---

        Simplest validation possible. Rest is for the frontenders
        """
        if len(password) > 4:
            return True
        else:
            self.logger.log_message(f"Error: Password validation for '{user_name}' failed.")
            return False

    def _validate_user_name(self, user_name:str):
        """
        --- logging ---
        Simplest validations for a user_name
        """
        if len(user_name) > 4:
            return True
        else:
            self.logger.log_message(f"Error: Username '{user_name}' validation failed.")
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
        return self._counter("user_statuses", status)

    
    def has_status(self, status):
        return self._is_status_of("user", status)

    
    def has(self, user_name):
        return self._is("user_id", "users", "user_name", user_name)

    
    def status_of(self, user_name: str):
        """
        -- logging --
        if user_name is incorrect returns False
        """
        if not self.has(user_name):
            self.logger.log_message(f"Error: Attempt to check status of an nonexisting user '{user_name}'.")
            return False
        return self._status_getter("user_status", "users", "user_name", "user_statuses", user_name)

    
    def get_info(self, user_name: str):
        """
        Returns user information as a dictionary for the given user_name.
        If the user does not exist, an empty dictionary is returned (equivalent to False).
        """
        user_info_dict = {}

        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT user_id, user_status, created_at, updated_at, n_samples_collected
                FROM users
                WHERE user_name = %s
            """, (user_name,))
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
        Returns a dictionary where the keys are user_names and the values are
        the corresponding user information dictionaries.
        """
        all_users_dict = {}

        with self.db as (conn, cursor):
            cursor.execute("SELECT user_name FROM users")
            user_names = cursor.fetchall()

        for user_name_tuple in user_names:
            user_name = user_name_tuple[0]
            user_info_dict = self.get_info(user_name)
            all_users_dict[user_name] = user_info_dict

        return all_users_dict

    
    def new(self, user_name:str, password:str):
        """
        -- logging --
        Returns the user_id if successful, otherwise False.
        """
        if self.has(user_name):
            self.logger.log_message(f"Error: Username '{user_name}' is already taken.")
            return False
        if not self._validate_user_name(user_name):
            return False
        if not self._validate_password(password, user_name):
            return False
        
        password_hash, salt = self._hash_and_salt(password)

        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO users (user_name, user_status, password_hash, password_salt)
                VALUES (%s, 3, %s, %s)
                RETURNING user_id
            """, (user_name, password_hash, salt))
            user_id = cursor.fetchone()[0]
            cursor.execute("UPDATE user_statuses SET n = n + 1 WHERE status_id = 3")
            conn.commit()
        self.logger.log_message(f"Info : User #{user_id} '{user_name}' has been created")
        return user_id 

    
    def change_status(self, user_name, new_status):
        return self._change_status("user_name", "users", "user_status", "user_statuses", user_name, new_status)

    
    def change_name(self, old_user_name: str, new_user_name: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.has(old_user_name):
            self.logger.log_message(f"Error: Can't change user_name of a nonexisting user '{old_user_name}'.")
            return False
        
        if old_user_name==new_user_name:
            # No user_name change, no logging
            return old_user_name

        if self.has(new_user_name):
            self.logger.log_message(f"Error: Can't change user_name '{old_user_name}' to '{new_user_name}' - the name is taken.")
            return False

        if not self._validate_user_name(new_user_name):
            return False
        
        with self.db as (conn, cursor):
            cursor.execute("UPDATE users SET user_name = %s WHERE user_name = %s", (new_user_name, old_user_name))
            conn.commit()
            
        self.logger.log_message(f"Info : User '{old_user_name}' changed name to '{new_user_name}'.")
        return new_user_name

    
    def change_user_password(self, user_name: str, new_password: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.has(user_name):
            self.logger.log_message(f"Error: Can't change password of a nonexisting user '{user_name}'.")
            return False
        
        if not self._validate_password(new_password, user_name):
            return False
        
        with self.db as (conn, cursor):
            hashed_password, salt = self._hash_and_salt(new_password)
            cursor.execute("""
                UPDATE users
                SET password_hash = %s, password_salt = %s
                WHERE user_name = %s;
            """, (hashed_password, salt, user_name))
            conn.commit()
        self.logger.log_message(f"Info : Changed password for user '{user_name}'.")
        return True

    
    def password_match(self, user_name: str, password: str):
        """
        -- logging --
        """
        if not self.has(user_name):
            self.logger.log_message(f"Error: Authentication attempt for nonexisting user_name '{user_name}'.")
            return False

        with self.db as (conn, cursor):
            cursor.execute("SELECT password_hash, password_salt FROM users WHERE user_name = %s", (user_name,))
            stored_hash, stored_salt = cursor.fetchone()
        rehashed_password = self._hashing(password.encode('utf-8'), stored_salt)

        return rehashed_password == bytes(stored_hash)