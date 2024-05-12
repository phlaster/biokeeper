from abc import ABC, abstractmethod

from DBConnection import DBConnection
from Logger import Logger

class AbstractDBManager(ABC):
    def __init__(self, logdata, logfile="logs.log"):
        self.logdata = logdata
        self.db = DBConnection(logdata)
        self.logfile = logfile
        self.logger = Logger(logfile)
    
    def _counter(self, table_name:str, obj_status:str, statuses_table:str, status:str):
        with self.db as (conn, cursor):
            if status == "all":
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            else:
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM {table_name} 
                    WHERE {obj_status} IN (
                        SELECT status_id 
                        FROM {statuses_table} 
                        WHERE status_key = %s
                    )
                """, (status,))
            result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

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
                return False
        if result:
            return result
        else:
            return False

    def _is(self, identifier_id:str, table:str, column:str, identifier:str):
        """
        returns research_id if successfull
        """
        with DBConnection(self.logdata) as (conn, cursor):
            cursor.execute(f"SELECT {identifier_id} FROM {table} WHERE {column} = %s", (identifier,))
            result = cursor.fetchone()
        return result[0] if result is not None else False

    def _status_getter(self, status_column:str, obj_table:str, identifier_name:str, status_table:str, identifier:str):
        """
        -- logging --
        if username is incorrect returns False
        """
        with self.db as (conn, cursor):
            cursor.execute(f"SELECT {status_column} FROM {obj_table} WHERE {identifier_name} = %s", (identifier,))
            status_id = cursor.fetchone()
            cursor.execute(f"SELECT status_key FROM {status_table} WHERE status_id = %s", (status_id,))
            status_key = cursor.fetchone()[0]
        return status_key


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

        if result:
            return {'qr_id': int(result[0]), 'is_used': bool(result[1]), 'kit_id': int(result[2])}
        else:
            return {}



