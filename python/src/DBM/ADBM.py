from abc import ABC, abstractmethod

from DBConnection import DBConnection
from Logger import Logger

class AbstractDBManager(ABC):
    def __init__(self, logdata, logfile="logs.log"):
        self.logdata = logdata
        self.db = DBConnection(logdata)
        self.logfile = logfile
        self.logger = Logger(logfile)
    
    def _counter(self, table_name:str, status_key:str):
        with self.db as (conn, cursor):
            if status_key == 'all':
                cursor.execute(f"SELECT SUM(n) FROM {table_name};")
            else:
                cursor.execute(f"SELECT n FROM {table_name} WHERE status_key = %s;", (status_key,))
            result = cursor.fetchone()[0]
        return result

    def _is_status_of(self, table_prefix:str, status:str):
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
                return ()
        
        return result if result else ()
        # if result:
        #     return result
        # else:
        #     return ()

    def _is(self, identifier_id:str, table:str, column:str, identifier:str):
        """
        returns research_id if successfull
        """
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute(f"SELECT {identifier_id} FROM {table} WHERE {column} = %s", (identifier,))
            result = cursor.fetchone()
        return result[0] if result else 0

    def _status_getter(self, status_column:str, obj_table:str, identifier_name:str, status_table:str, identifier:str):
        """
        -- logging --
        if user_name is incorrect returns False
        """
        with self.db as (conn, cursor):
            cursor.execute(f"SELECT {status_column} FROM {obj_table} WHERE {identifier_name} = %s", (identifier,))
            status_id = cursor.fetchone()
            cursor.execute(f"SELECT status_key FROM {status_table} WHERE status_id = %s", (status_id,))
            status_key = cursor.fetchone()[0]
        return status_key

    def _change_status(self, identifier_name, identifier_table, status_column, statuses_table, identifier, new_status):
        """
        -- logging --
        returns False if unsuccessfull
        """
        if not self.has(identifier):
            if identifier == "kit":
                self.logger.log_message(f"Error: No such {identifier_name.split('_')[0]} '{identifier}'.")
            else:
                self.logger.log_message(f"Error: Kit #{identifier} does not exist.")
            return ""

        new_status_query = self.has_status(new_status)
        if not new_status_query:
            self.logger.log_message(f"Error: Status '{new_status}' is not a valid {identifier_name.split('_')[0]} status.")
            return ""
        new_status_id = new_status_query[0]

        current_status = self.status_of(identifier)
        current_status_id = self.has_status(current_status)[0]

        if new_status_id == current_status_id:
            # No status change, no logging
            return new_status

        with self.db as (conn, cursor):
            cursor.execute(f"UPDATE {identifier_table} SET {status_column} = %s WHERE {identifier_name} = %s", (new_status_id, identifier))
            cursor.execute(f"UPDATE {statuses_table} SET n = n - 1 WHERE status_id = %s", (current_status_id,))
            cursor.execute(f"UPDATE {statuses_table} SET n = n + 1 WHERE status_id = %s", (new_status_id,))
            conn.commit()

        self.logger.log_message(f"Info : Research '{identifier}' status changed to '{new_status}'")
        return new_status

    def _all_getter(self, identifier_name, table_name):
        """
        Returns a dictionary where keys are identifiers
        and values are the result of .get_info call for each identifier.
        """
        alls = {}

        with self.db as (conn, cursor):
            cursor.execute(f"SELECT {identifier_name} FROM {table_name}")
            all_identifiers = cursor.fetchall()

        for tpl in all_identifiers:
            obj_id = tpl[0]
            kit_info = self.get_info(obj_id)
            alls[obj_id] = kit_info

        return alls
    
    @abstractmethod
    def count(self, status):
        pass

    @abstractmethod
    def has_status(self, status):
        pass

    @abstractmethod
    def has(self, identifier):
        pass

    @abstractmethod
    def status_of(self, identifier):
        pass

    @abstractmethod
    def get_info(self, identifier):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def new(self, *args, **kwargs):
        pass

    @abstractmethod
    def change_status(self, identifier, new_status):
        pass


    def clear_logs(self):
        self.logger.clear_logs()

    def get_qr_info(self, qr_bytes: bytes):
        """
        returns dict with QR info if successfull
        empty dict otherwise
        """
        with self.db as (conn, cursor):
            cursor.execute("SELECT qr_id, is_used, kit_id FROM qrs WHERE qr_unique_code = %s", (qr_bytes,))
            result = cursor.fetchone()

        return {'qr_id': int(result[0]), 'is_used': bool(result[1]), 'kit_id': int(result[2])} if result else {}



