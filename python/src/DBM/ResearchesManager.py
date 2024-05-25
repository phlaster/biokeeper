from DBM.ADBM import AbstractDBManager
from DBM.UsersManager import UsersManager
import datetime
from multimethod import multimethod

class ResearchesManager(AbstractDBManager):
    def count(self, status:str="all"):
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
        id = self.has(identifier)
        if not id:
            return self.logger.log(f"Error: Research '{identifier}' does not exist.", "") if log else ""
        return self._status_getter("research", id)

    
    def get_info(self, identifier, log=False):
        research_info_dict = {}
        research_id = self.has(identifier)
        if not research_id:
            return self.logger.log(f"Error: Research '{identifier}' does not exist.", research_info_dict) if log else research_info_dict

        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT name, created_at, updated_at, created_by, day_start, day_end, n_samples, comment
                FROM "research"
                WHERE id = %s
            """, (research_id,))
            research_data = cursor.fetchone()

        if research_data:
            research_info_dict['name'] = research_data[0]
            research_info_dict['id'] = research_id
            research_info_dict['status'] = self.status_of(identifier)
            research_info_dict['created_at'] = research_data[1].astimezone().isoformat()
            research_info_dict['updated_at'] = research_data[2].astimezone().isoformat()
            research_info_dict['created_by'] = research_data[3]
            research_info_dict['day_start'] = research_data[4].strftime("%Y-%m-%d")
            research_info_dict['day_end'] = research_data[5].strftime("%Y-%m-%d") if research_data[5] else None
            research_info_dict['n_samples'] = research_data[6]
            research_info_dict['comment'] = research_data[7]

        return research_info_dict


    def get_all(self):
        return self._all_getter("id", "research")

    
    def new(self, research_name: str, user_name: str, day_start: datetime.date, research_comment: str = None, log=False):
        if self.has(research_name):
            return self.logger.log(f"Error: Research '{research_name}' is already exists.", 0) if log else 0

        users = UsersManager(self.logdata, logfile=self.logfile)
        user_id = users.has(user_name)
        if not user_id:
            return self.logger.log(f"Error: Can't assign new research '{research_name}' to a nonexisting user '{user_name}'.", 0) if log else 0

        user_status = users.status_of(user_name) # Careful here!
        if user_status != "admin":
            return self.logger.log(f"Error: User '{user_name}' of status '{user_status}' has no privilege to create researches.", 0) if log else 0

        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO "research"
                (name, comment, created_by, day_start)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (research_name, research_comment, user_id, day_start))
            research_id = cursor.fetchone()[0]
            conn.commit()
        log and self.logger.log(f"Info : Created research #{research_id} '{research_name}' starting on {day_start} by '{user_name}'", research_id)
        return research_id

    
    def change_status(self, identifier, new_status, log=False):
        return self._change_status("research", identifier, new_status, log)

    
    def change_comment(self, identifier, comment: str, log=False):
        research_id = self.has(identifier)
        if not research_id:
            return self.logger.log(f"Error: Research '{identifier}' does not exist.", 0) if log else 0

        with self.db as (conn, cursor):
            cursor.execute("""
                UPDATE "research"
                SET comment = %s
                WHERE id = %s
            """, (comment, research_id))
            conn.commit()
        log and self.logger.log(f"Info : Updated comment for research #{research_id}", research_id)
        return research_id

    
    def change_day_end(self, identifier, day_end: datetime.date, log=False):
        research_id = self.has(identifier)
        if not research_id:
            return self.logger.log(f"Error: Research '{identifier}' does not exist.", 0) if log else 0

        with self.db as (conn, cursor):
            day_start = self._SELECT("day_start", "research", "id", research_id)

            if day_end < day_start:
                return self.logger.log(f"Error: Can't set ending day at {day_end} for research #{research_id} that starts on {day_start}.", 0) if log else 0

            cursor.execute("""
                UPDATE "research"
                SET day_end = %s
                WHERE id = %s
            """, (day_end, research_id))
            conn.commit()

        log and self.logger.log(f"Info : Now research #{research_id} ends on {day_end}", research_id)
        return research_id