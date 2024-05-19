from DBM.ADBM import AbstractDBManager
from DBM.UsersManager import UsersManager
import datetime
from multimethod import multimethod

class ResearchesManager(AbstractDBManager):
    def count(self, status:str="all"):
        """
        Currently possible statuses: "pending", "ongoing", "paused", "ended", "cancelled"
        """
        return self._counter("research_statuses", status)

    @multimethod
    def has_status(self, status: str):
        return self._is_status_of("research", status)

    @multimethod
    def has(self, research_name: str, log=False):
        id = self._SELECT("id", "research", "name", research_name)
        if not id:
            return self.logger.log(f"Error: No such research '{research_name}'.", 0) if log else 0
        return id
    
    @multimethod
    def has(self, research_id: int, log=False):
        id = self._SELECT("id", "research", "id", research_id)
        if not id:
            return self.logger.log(f"Error: No such research #{research_id}.", 0) if log else 0
        return id

    
    def status_of(self, identifier, log=False):
        """
        Returns the status key of the research with the given name.
        If the research does not exist, False is returned.
        """
        id = self.has(identifier)
        if not id:
            return self.logger.log(f"Error: Research '{identifier}' does not exist.", "") if log else ""
        return self._status_getter("research", id)

    
    def get_info(self, research_name: str, log=False):
        """
        Returns research information as a dictionary for the given research name.
        If the research does not exist, an empty dictionary is returned (equivalent to False).
        """
        research_info_dict = {}
        if not self.has(research_name):
            return self.logger.log(f"Error: Research '{research_name}' does not exist.", research_info_dict) if log else research_info_dict

        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT id, status, created_at, updated_at, created_by, day_start, day_end, n_samples, comment
                FROM "research"
                WHERE name = %s
            """, (research_name,))
            research_data = cursor.fetchone()

        if research_data:
            research_info_dict['research_id'] = research_data[0]
            research_info_dict['research_status'] = self.status_of(research_name)
            research_info_dict['created_at'] = research_data[2].strftime("%Y-%m-%d, %H:%M:%S")
            research_info_dict['updated_at'] = research_data[3].strftime("%Y-%m-%d, %H:%M:%S")
            research_info_dict['created_by'] = research_data[4]
            research_info_dict['day_start'] = research_data[5].strftime("%Y-%m-%d")
            research_info_dict['day_end'] = research_data[6].strftime("%Y-%m-%d") if research_data[6] else None
            research_info_dict['n_samples'] = research_data[7]
            research_info_dict['research_comment'] = research_data[8]

        return research_info_dict


    def get_all(self):
        return self._all_getter("name", "research")

    
    def new(self, research_name: str, user_name: str, day_start: datetime.date, research_comment: str = None, log=False):
        """
        -- logging --
        Returns the research_id if successful, otherwise False.
        """
        if self.has(research_name):
            return self.logger.log(f"Error: Research '{research_name}' is already exists.", False) if log else False

        users = UsersManager(self.logdata, logfile=self.logfile)
        user_id = users.has(user_name)
        if not user_id:
            return self.logger.log(f"Error: Can't assign new research '{research_name}' to a nonexisting user '{user_name}'.", False) if log else False

        user_status = users.status_of(user_name) # Careful here!
        if user_status != "admin":
            return self.logger.log(f"Error: User '{user_name}' of status '{user_status}' has no privilege to create researches.", False) if log else False

        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO "research"
                (name, comment, created_by, day_start)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (research_name, research_comment, user_id, day_start))
            research_id = cursor.fetchone()[0]
            conn.commit()
        return self.logger.log(f"Info : Research #{research_id} '{research_name}' starting on {day_start} created by '{user_name}'", research_id) if log else research_id

    
    def change_status(self, identifier, new_status, log=False):
        return self._change_status("research", identifier, new_status, log)

    
    def change_comment(self, research_name: str, comment: str, log=False):
        if not self.has(research_name):
            return self.logger.log(f"Error: Research '{research_name}' does not exist.", False) if log else False

        with self.db as (conn, cursor):
            cursor.execute("""
                UPDATE "research"
                SET comment = %s
                WHERE name = %s
            """, (comment, research_name))
            conn.commit()

        return self.logger.log(f"Info : Updated comment for research '{research_name}'", True) if log else True

    
    def change_day_end(self, research_name: str, day_end: datetime.date, log=False):
        if not self.has(research_name):
            return self.logger.log(f"Error: Research '{research_name}' does not exist.", False) if log else False

        with self.db as (conn, cursor):
            day_start = self._SELECT("day_start", "research", "name", research_name)

            if day_end < day_start:
                return self.logger.log(f"Error: Can't set ending day at {day_end} for research '{research_name}' that starts on {day_start}.", False) if log else False

            cursor.execute("""
                UPDATE "research"
                SET day_end = %s
                WHERE name = %s
            """, (day_end, research_name))
            conn.commit()

        return self.logger.log(f"Info : Now '{research_name}' ends on {day_end}", True) if log else True