from ADBM import AbstractDBManager
from UsersManager import UsersManager
import datetime

class ResearchesManager(AbstractDBManager):
    def count(self, status:str="all"):
        """
        Returns number of researches with different statuses.
        'all' for all statuses OR
        Currently possible statuses: "pending", "ongoing", "paused", "ended", "cancelled"
        """
        return self._counter("researches", "research_status", "research_statuses", status)

    def has_status(self, status):
        return self._is_status_of("research", status)

    def has(self, research_name):
        return self._is("research_id", "researches", "research_name", research_name)

    def status_of(self, research_name):
        """
        Returns the status key of the research with the given name.
        If the research does not exist, False is returned.
        """
        if not self.has(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' does not exist.")
            return False
        return self._status_getter("research_status", "researches", "research_name", "research_statuses", research_name)

    def get_info(self, research_name: str):
        """
        Returns research information as a dictionary for the given research name.
        If the research does not exist, an empty dictionary is returned (equivalent to False).
        """
        research_info_dict = {}
        if not self.has(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' does not exist.")
            return research_info_dict

        with self.db as (conn, cursor):
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

    def get_all(self):
        """
        Returns a dictionary where the keys are research names and the values are
        the corresponding research information dictionaries.
        """
        all_researches_dict = {}

        with self.db as (conn, cursor):
            cursor.execute("SELECT research_name FROM researches")
            research_names = cursor.fetchall()

        for research_name in research_names:
            research_info_dict = self.get_info(research_name[0])
            all_researches_dict[research_name[0]] = research_info_dict

        return all_researches_dict 

    def new(self, research_name: str, username: str, day_start: datetime.date, research_comment: str = None):
        """
        -- logging --
        Returns the research_id if successful, otherwise False.
        """
        if self.has(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' is already exists.")
            return False

        users = UsersManager(self.logdata, logfile=self.logfile)
        user_id = users.has(username)
        if not user_id:
            self.logger.log_message(f"Error: Can't assign new research '{research_name}' to a nonexisting user '{username}'.")
            return False

        user_status = users.status_of(username) # Careful here!
        if user_status != "admin":
            self.logger.log_message(f"Error: User '{username}' of status '{user_status}' has no privilege to create researches.")
            return False

        with self.db as (conn, cursor):
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

    def change_status(self, research_name: str, new_status: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.has(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' does not exist.")
            return False

        new_status_query = self.has_status(new_status)
        if not new_status_query:
            self.logger.log_message(f"Error: Status '{new_status}' is not a valid research status.")
            return False
        new_status_id = new_status_query[0]

        current_status = self.status_of(research_name)
        current_status_id = self.has_status(current_status)[0]

        if new_status_id == current_status_id:
            # No status change, no logging
            return new_status

        with self.db as (conn, cursor):
            cursor.execute("UPDATE researches SET research_status = %s WHERE research_name = %s", (new_status_id, research_name))
            conn.commit()

        self.logger.log_message(f"Info : Research '{research_name}' status changed to '{new_status}'")
        return new_status

    def change_comment(self, research_name: str, comment: str):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.has(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' does not exist.")
            return False

        with self.db as (conn, cursor):
            cursor.execute("UPDATE researches SET research_comment = %s WHERE research_name = %s", (comment, research_name))
            conn.commit()

        self.logger.log_message(f"Info : Updated comment for research '{research_name}'")
        return True

    def change_day_end(self, research_name: str, day_end: datetime.date):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.has(research_name):
            self.logger.log_message(f"Error: Research '{research_name}' does not exist.")
            return False

        with self.db as (conn, cursor):
            cursor.execute("SELECT day_start FROM researches WHERE research_name = %s", (research_name,))
            day_start = cursor.fetchone()[0]

            if day_end < day_start:
                self.logger.log_message(f"Error: Can't set ending day at {day_end} for research '{research_name}' that starts on {day_start}.")
                return False

            cursor.execute("UPDATE researches SET day_end = %s WHERE research_name = %s", (day_end, research_name))
            conn.commit()

        self.logger.log_message(f"Info : Now '{research_name}' ends on {day_end}")
        return True