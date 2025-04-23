import requests
from DBM.ADBM import AbstractDBManager
import hashlib
import os
from multimethod import multimethod
from exceptions import NoUserException
from utils import validate_return_from_db

class UsersManager(AbstractDBManager):
    @multimethod
    def count(self, status: str = "all"):
        # TODO:
        # get count of statuses from other services
        pass

    @multimethod
    def change_status(self, identifier, new_status, log=False):
        # TODO:
        # change status using other services
        pass

    @multimethod
    def has_status(self, status: str):
        # TODO:
        # Check status using other services

        # return self._is_status_of("user", status)
        pass

    @multimethod
    def has(self, user_name: str, log=False):
        id = self._SELECT("id", "user", "name", user_name)
        return validate_return_from_db({"user": id},
                                       "user_name",
                                       user_name,
                                       self.logger if log else None,
                                       NoUserException)
    
    @multimethod
    def has(self, user_id: int, log=False):
        id = self._SELECT("id", "user", "id", user_id)
        return validate_return_from_db({"user": id},
                                       "user_id",
                                       user_id,
                                       self.logger if log else None,
                                       NoUserException)
    

    def status_of(self, identifier, log=False):
        # TODO:
        # Check status using other services

        user_id = self.has(identifier, log=log)
        if not user_id:
            raise UserNotFoundException
        # make request to http://auth_backend:8000/users/{user_id}/role and get name from response
        request_url = f"http://auth_backend:8000/users/{user_id}/role"
        response = requests.get(request_url)
        user_status = response.json()
        status_name = user_status.get('name')
        return status_name
    
    def _get_created_at(self, identifier):
        # TODO:
        # get created_at from other services
        # use .astimezone().isoformat()
        user_id = self.has(identifier)
        if not user_id:
            raise UserNotFoundException

        # make request to http://auth_backend:8000/users/{user_id}/status and get name from response
        request_url = f"http://auth_backend:8000/users/{user_id}/created_at"
        response = requests.get(request_url)
        created_at = response.json().get('created_at')
        return created_at
    def get_info(self, identifier):
        # TODO:
        user_info_dict = {}

        user_id = self.has(identifier)
        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT name, updated_at, n_samples_collected
                FROM "user"
                WHERE id = %s
            """, (user_id,))
            user_data = cursor.fetchone()

        if user_data:
            user_info_dict['id'] = user_id
            user_info_dict['name'] = user_data[0]
            user_info_dict['status'] = self.status_of(identifier)
            user_info_dict['created_at'] = self._get_created_at(identifier)
            user_info_dict['updated_at'] = user_data[1].astimezone().isoformat()
            user_info_dict['n_samples_collected'] = user_data[2]
        return user_info_dict

    def get_all(self):
        return self._all_getter("name", "user")

    @multimethod
    def new(self, id, user_name: str, log=False):
    # TODO: fetching created users from auth_service
        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO "user"
                (id, name)
                VALUES (%s, %s)
                RETURNING id
            """, (id, user_name))
            conn.commit()
            log and self.logger.log(f"Info : User #{id} '{user_name}' has been added to the system", id)
        return id
    
    def get_user_participated_researches(self, identifier, log=False):
        user_id = self.has(identifier)
        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT research_id
                FROM "user_research"
                WHERE user_id = %s
            """, (user_id,))
            researches = cursor.fetchall()

        if not researches:
            return []

        return researches[0]
    
    # def get_user_qrs(self, identifier, log=False):
    #     user_id = self.has(identifier)
    #     with self.db as (conn, cursor):
    #         cursor.execute("""
    #             SELECT id
    #             FROM "qr"
    #             WHERE user_id = %s
    #         """, (user_id,))
    #         qrs = cursor.fetchall()[0]

    #     return qrs

    # @multimethod
    # def rename(self, user_identifier, new_user_name: str, log=False):
    #     TODO: call other services to apply changes there too
    #     user_id =  self.has(user_identifier, log=log)
    #     if not user_id:
    #         return self.logger.log(f"Error: Can't change user_name of a nonexisting user '{user_identifier}'.", "") if log else ""
        
    #     new_username_id = self.has(new_user_name)
    #     if user_id==new_username_id:
    #         return new_user_name

    #     if new_username_id:
    #         return self.logger.log(f"Error: Can't change user_name for user #{user_id} to '{new_user_name}' - the name is taken.", "") if log else ""

    #     if not self._validate_user_name(new_user_name, log=log):
    #         return ""
        
    #     with self.db as (conn, cursor):
    #         cursor.execute('UPDATE "user" SET name = %s WHERE id = %s', (new_user_name, user_id))
    #         conn.commit()
            
    #     log and self.logger.log(f"Info : User #{user_id} changed name to '{new_user_name}'.", new_user_name)
    #     return new_user_name
