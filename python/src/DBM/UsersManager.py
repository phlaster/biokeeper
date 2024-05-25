from DBM.ADBM import AbstractDBManager
import hashlib
import os
from multimethod import multimethod


class UsersManager(AbstractDBManager):
    @multimethod
    def _validate_password(self, password: str, identifier: str, log=False):
        if len(password) > 4:
            return True
        else:
            return self.logger.log(f"Error: Password validation for '{identifier}' failed.", False) if log else False
    
    @multimethod
    def _validate_user_name(self, user_name: str, log=False):
        if len(user_name) > 4:
            return True
        else:
            return self.logger.log(f"Error: Username '{user_name}' validation failed.", False) if log else False
    
    @multimethod
    def _hashing(self, password: str, salt: str) -> str:
        password_encoded = password.encode('utf-8')
        salt_encoded = bytes.fromhex(salt)
        return hashlib.scrypt(password_encoded, salt=salt_encoded, n=2**14, r=8, p=1).hex()
    
    @multimethod
    def _hash_and_salt(self, password: str) -> tuple[str, str]:
        salt = os.urandom(16).hex()
        hashed = self._hashing(password, salt)
        return (hashed, salt)

    def count(self, status: str = "all"):
        return self._counter("user_statuses", status)

    @multimethod
    def has_status(self, status: str):
        return self._is_status_of("user", status)

    @multimethod
    def has(self, user_name: str, log=False):
        id = self._SELECT("id", "user", "name", user_name)
        if not id:
            return self.logger.log(f"Error: No such user '{user_name}'.", 0) if log else 0
        return id
    
    @multimethod
    def has(self, user_id: int, log=False):
        id = self._SELECT("id", "user", "id", user_id)
        if not id:
            return self.logger.log(f"Error: No such user #{user_id}.", 0) if log else 0
        return id

    def status_of(self, identifier, log=False):
        user_id = self.has(identifier, log=log)
        if not user_id:
            return ""
        return self._status_getter("user", user_id)

    def get_info(self, identifier):
        user_info_dict = {}

        user_id = self.has(identifier)
        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT name, created_at, updated_at, n_samples_collected
                FROM "user"
                WHERE id = %s
            """, (user_id,))
            user_data = cursor.fetchone()

        if user_data:
            user_info_dict['id'] = user_id
            user_info_dict['name'] = user_data[0]
            user_info_dict['status'] = self.status_of(identifier)
            user_info_dict['created_at'] = user_data[1].astimezone().isoformat()
            user_info_dict['updated_at'] = user_data[2].astimezone().isoformat()
            user_info_dict['n_samples_collected'] = user_data[3]
        return user_info_dict

    def get_all(self):
        return self._all_getter("name", "user")

    @multimethod
    def new(self, user_name: str, password: str, log=False):
        if self.has(user_name, log=log):
            return False
        if not self._validate_user_name(user_name, log=log):
            return False
        if not self._validate_password(password, user_name, log=log):
            return False
        
        password_hash, salt = self._hash_and_salt(password)

        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO "user"
                (name, password_hash, password_salt)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (user_name, password_hash, salt))
            user_id = cursor.fetchone()[0]
            conn.commit()
        log and self.logger.log(f"Info : User #{user_id} '{user_name}' has been created", user_id)
        return user_id

    @multimethod
    def change_status(self, identifier, new_status: str, log=False):
        return self._change_status("user", identifier, new_status, log=log)


    @multimethod
    def rename(self, user_identifier, new_user_name: str, log=False):
        user_id =  self.has(user_identifier, log=log)
        if not user_id:
            return self.logger.log(f"Error: Can't change user_name of a nonexisting user '{user_identifier}'.", "") if log else ""
        
        new_username_id = self.has(new_user_name)
        if user_id==new_username_id:
            return new_user_name

        if new_username_id:
            return self.logger.log(f"Error: Can't change user_name for user #{user_id} to '{new_user_name}' - the name is taken.", "") if log else ""

        if not self._validate_user_name(new_user_name, log=log):
            return ""
        
        with self.db as (conn, cursor):
            cursor.execute('UPDATE "user" SET name = %s WHERE id = %s', (new_user_name, user_id))
            conn.commit()
            
        log and self.logger.log(f"Info : User #{user_id} changed name to '{new_user_name}'.", new_user_name)
        return new_user_name

    
    @multimethod
    def change_user_password(self, identifier, new_password: str, log=False):
        user_id = self.has(identifier, log=log)
        if not user_id:
            return self.logger.log(f"Error: Can't change password of a nonexisting user '{identifier}'.", 0) if log else 0
        
        if not self._validate_password(new_password, identifier, log=log):
            return 0
        
        with self.db as (conn, cursor):
            hashed_password, salt = self._hash_and_salt(new_password)
            cursor.execute("""
                UPDATE "user"
                SET password_hash = %s, password_salt = %s
                WHERE id = %s;
            """, (hashed_password, salt, user_id))
            conn.commit()
        log and self.logger.log(f"Info : Changed password for user #{user_id}.", user_id)
        return user_id

    
    def password_match(self, identifier, password: str, log=False):
        user_id = self.has(identifier, log=log)
        if not user_id:
            return self.logger.log(f"Error: Authentication attempt for nonexisting user '{identifier}'.", 0) if log else 0

        with self.db as (conn, cursor):
            cursor.execute('SELECT password_hash, password_salt FROM "user" WHERE id = %s', (user_id,))
            stored_hash, stored_salt = cursor.fetchone()
        rehashed_password = self._hashing(password, stored_salt)

        return user_id if rehashed_password == stored_hash else 0
