from DBM.ADBM import AbstractDBManager
from DBM.UsersManager import UsersManager
import datetime
from exceptions import NoResearchException
from multimethod import multimethod
from utils import validate_return_from_db

class ResearchesManager(AbstractDBManager):
    def count(self, status:str="all"):
        return self._counter("research_statuses", status)

    @multimethod
    def has_status(self, status: str):
        return self._is_status_of("research", status)

    @multimethod
    def has(self, research_name: str, log=False):
        id = self._SELECT("id", "research", "name", research_name)
        return validate_return_from_db({"research": id},
                                       "research_name",
                                       research_name,
                                       self.logger if log else None,
                                       NoResearchException)
    
    @multimethod
    def has(self, research_id: int, log=False):
        id = self._SELECT("id", "research", "id", research_id)
        return validate_return_from_db({"research": id},
                                       "research_id",
                                       research_id,
                                       self.logger if log else None,
                                       NoResearchException)

    
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
                SELECT name, created_at, updated_at, created_by, day_start, day_end, n_samples, comment, approval_required
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
            research_info_dict['approval_required'] = research_data[8]

        return research_info_dict


    def get_all(self):
        return self._all_getter("id", "research")

    
    def new(self, research_name: str, user_id: int, day_start: datetime.date, research_comment: str = None, log=False, approval_required=True):
        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO "research"
                (name, comment, created_by, day_start,approval_required)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (research_name, research_comment, user_id, day_start, approval_required))
            research_id = cursor.fetchone()[0]
            conn.commit()
        log and self.logger.log(f"Info : Created research #{research_id} '{research_name}' starting on {day_start} by user with id '{user_id}'. Approval required: {approval_required}", research_id)
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
    
    def get_participants_ids(self, research_id, log=False):
        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT user_id
                FROM "user_research"
                WHERE research_id = %s
            """, (research_id,))
            participants = cursor.fetchall()
            if participants:
                participants = participants[0]
            else:
                participants = []

        return participants

    def get_candidates_ids(self, research_id, log=False):
        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT user_id
                FROM "user_research_pending"
                WHERE research_id = %s
            """, (research_id,))
            candidates = cursor.fetchall()
            if candidates:
                candidates = candidates[0]
            else:
                candidates = []

        return candidates
    
    def get_pending_requests(self, research_id, log=False):
        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT urp.user_id, u.name as username
                FROM "user_research_pending" urp
                LEFT JOIN "user" u ON urp.user_id = u.id
                WHERE research_id = %s
            """, (research_id,))
            pending = cursor.fetchall()
            if pending:
                pending = [{'user_id': user_id, 'username': username} for user_id, username in pending]
            else:
                pending = []
        return pending

    def get_accepted_participants(self, research_id, log=False):
        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT ur.user_id, u.name as username
                FROM "user_research" ur
                LEFT JOIN "user" u ON ur.user_id = u.id
                WHERE research_id = %s
            """, (research_id,))
            accepted = cursor.fetchall()
            if accepted:
                accepted = [{'user_id': user_id, 'username': username} for user_id, username in accepted]
            else:
                accepted = []
        return accepted
    
    def send_request(self, research_id, user_id, log=False):
        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO "user_research_pending"
                (research_id, user_id)
                VALUES (%s, %s)
            """, (research_id, user_id))
            conn.commit()

    def approve_request(self, research_id, user_id, log=False):
        with self.db as (conn, cursor):
            cursor.execute("""
                DELETE FROM "user_research_pending"
                WHERE research_id = %s AND user_id = %s
            """, (research_id, user_id))

            cursor.execute("""
                INSERT INTO "user_research"
                (research_id, user_id)
                VALUES (%s, %s)
            """, (research_id, user_id))

            conn.commit()

    def decline_request(self, research_id, user_id, log=False):
        with self.db as (conn, cursor):
            cursor.execute("""
                DELETE FROM "user_research_pending"
                WHERE research_id = %s AND user_id = %s
            """, (research_id, user_id))
            conn.commit()

    def get_researches_by_user_identifier(self, user_identifier):

        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT research_id
                FROM "user_research"
                WHERE user_id = %s
            """, (user_identifier,))
            researches = cursor.fetchall()
            if researches:
                researches = researches[0]
            else:
                researches = []
            researches = [{'research_id': research_id} for research_id in researches]
        return researches

    def get_created_researches_by_user_identifier(self, user_identifier):

        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT r.id, r.name, (rs.details).key as status
                FROM "research" r
                LEFT JOIN "research_statuses" rs ON r.status = rs.id
                WHERE created_by = %s
            """, (user_identifier,))
            researches = cursor.fetchall()
            if researches:
                researches = [{'id': research[0], 'name': research[1], 'status': research[2]} for research in researches]
            else:
                researches = []
        return researches
    
    
    def delete_accepted_participant(self, research_id, user_id, log=False):
        with self.db as (conn, cursor):
            cursor.execute("""
                DELETE FROM "user_research"
                WHERE research_id = %s AND user_id = %s
            """, (research_id, user_id))
            conn.commit()