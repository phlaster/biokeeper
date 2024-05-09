from DBConnection import DBConnection
from Logger import Logger
import hashlib
import os

class DBManager:
    def __init__(self, logdata, logfile="logs.log"):
        self.logdata = logdata
        self.logger = Logger(logfile)

    def _validate_password(self, password:str):
        return len(password) > 4

    def _validate_username(self, username:str):
        return len(username) > 4

    def _hashing(self, password_bytes: bytes, salt: bytes):
        return hashlib.scrypt(password_bytes, salt=salt, n=2**14, r=8, p=1)

    def _hash_and_salt(self, password: str) -> tuple[bytes, bytes]:
        """
        Hashes a password with a salt using the scrypt algorithm.
        """
        salt = os.urandom(16)
        password_bytes = password.encode('utf-8')
        hashed = self._hashing(password_bytes, salt)
        return (hashed, salt)


    def n_users(self, status:str="all"):
        """
        Returns number of users with different statuses.
        'all' for all statuses OR
        currently possible: "observer", "volunteer", "admin"
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
        currently possible: "pending", "ongoing", "paused", "ended", "cancelled"
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
                        FROM user_statuses 
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
        currently possible: "created", "sent", "activated"
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
                        FROM user_statuses 
                        WHERE status_key = %s
                    )
                """, (status,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return 0

    def is_user(self, username: str):
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            return result is not None

    def new_user(self, username:str, password:str):
        username = str(username)
        password = str(password)

        with DBConnection(self.logdata) as (conn, cursor):
            if self.is_user(username):
                raise ValueError(f"Username '{username}' is already taken.")
            if not self._validate_username(username):
                raise ValueError(f"Username '{username}' validation failed.")
            if not self._validate_password(password):
                raise ValueError(f"Password validation failed.")

            password_hash, salt = self._hash_and_salt(password)

            cursor.execute("""
                INSERT INTO users (username, password_hash, password_salt)
                VALUES (%s, %s, %s)
                RETURNING user_id
            """, (username, password_hash, salt))
            user_id = cursor.fetchone()[0]
            conn.commit()
            self.logger.log_message(f"User #{user_id} `{username}` has been created")
            return user_id
    
    def user_status(self, username: str):
        with DBConnection(self.logdata) as (conn, cursor):
            # Check if the user exists
            cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            if not cursor.fetchone():
                raise ValueError(f"User '{username}' does not exist.")

            cursor.execute("SELECT user_status FROM users WHERE username = %s", (username,))
            user_status_id = cursor.fetchone()

            cursor.execute("SELECT status_key FROM user_statuses WHERE status_id = %s", (user_status_id,))
            status_key = cursor.fetchone()[0]

            return status_key

    def change_user_status(self, username: str, new_status: str):
        if not self.is_user(username):
            raise ValueError(f"User '{username}' does not exist.")
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT user_status FROM users WHERE username = %s", (username,))
            current_status_id = cursor.fetchone()[0]

            cursor.execute("SELECT status_id, status_key FROM user_statuses WHERE status_key = %s", (new_status,))
            new_status_query = cursor.fetchone()

            if not new_status_query:
                raise ValueError(f"Status '{new_status}' is not a valid status.")

            new_status_id = new_status_query[0]
            if new_status_id == current_status_id:
                return new_status

            cursor.execute("UPDATE users SET user_status = %s WHERE username = %s", (new_status_id, username))
            conn.commit()
            self.logger.log_message(f"User `{username}` changed status to {new_status}")
            return new_status

    def change_user_name(self, old_username: str, new_username: str):
        if not self.is_user(old_username):
            raise ValueError(f"User '{old_username}' does not exist.")
        
        if old_username==new_username:
            return old_username

        if self.is_user(new_username):
            raise ValueError(f"Username '{new_username}' is already taken.")

        if not self._validate_username(new_username):
            raise ValueError(f"Username '{new_username}' validation failed.")
        
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("UPDATE users SET username = %s WHERE username = %s", (new_username, old_username))
            conn.commit()
            
        self.logger.log_message(f"User `{old_username}` changed name to `{new_username}`")
        return new_username

    def password_match(self, username: str, password: str):
        if not self.is_user(username):
            raise ValueError(f"No such user `{username}`.")

        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("SELECT password_hash, password_salt FROM users WHERE username = %s", (username,))
            stored_hash, stored_salt = cursor.fetchone()
        rehashed_password = self._hashing(password.encode('utf-8'), stored_salt)

        return rehashed_password == bytes(stored_hash)

    def change_user_password(self, username: str, new_password: str):
        if not self.is_user(username):
            raise ValueError(f"User '{username}' does not exist.")
        
        if not self._validate_password(new_password):
            raise ValueError(f"Password validation failed.")
        
        with DBConnection(self.logdata) as (conn, cursor):
            hashed_password, salt = self._hash_and_salt(new_password)
            cursor.execute("""
                UPDATE users
                SET password_hash = %s, password_salt = %s
                WHERE username = %s;
            """, (hashed_password, salt, username))
            conn.commit()
        self.logger.log_message(f"User `{username}` changed password.")
        return True

    def all_users(self):
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute("""
                SELECT u.username, u.user_id, us.status_key, u.created_at, u.n_samples_collected
                FROM users u
                JOIN user_statuses us ON u.user_status = us.status_id
            """)
            result = cursor.fetchall()
        users_dict = {}
        for row in result:
            username, user_id, user_status, created_at, n_samples_collected = row
            users_dict[username] = {
                "user_id": user_id,
                "user_status": user_status,
                "created_at": created_at.date(),
                "n_samples_collected": n_samples_collected
            }
        return users_dict
