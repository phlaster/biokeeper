from abc import ABC, abstractmethod
from multimethod import multimethod
from DBM.DBConnection import DBConnection
from Logger import Logger

class AbstractDBManager(ABC):
    def __init__(self, logdata, logfile="logs.log"):
        self.logdata = logdata
        self.db = DBConnection(logdata)
        self.logfile = logfile
        self.logger = Logger(logfile)
    
    def _counter(self, table_name: str, status_key: str = "all"):
        with self.db as (conn, cursor):
            query = f"""
                SELECT SUM((details).n)
                FROM "{table_name}"
                {"" if status_key == "all" else "WHERE (details).key = %s"}
            """
            cursor.execute(query, (status_key,) if status_key != "all" else ())
            return cursor.fetchone()[0]

    def _is_status_of(self, table_prefix: str, status: str) -> tuple[int, str] | tuple:
        """
        Check if a given status exists for a table with given `table_prefix`.
        """
        table_name = f"{table_prefix}_statuses"
        query = f"""
            SELECT id, (details).info
            FROM {table_name}
            WHERE (details).key = %s;"""

        with self.db as (conn, cursor):
            cursor.execute(query, (status,))
            return cursor.fetchone() or ()

    def _SELECT(self, what:str, table:str, where:str, val):
        with self.db as (conn, cursor):
            cursor.execute(f"""
                SELECT {what}
                FROM "{table}"
                WHERE {where} = %s
            """, (val,))
            result = cursor.fetchone()
        return result[0] if result else None

    def _status_getter(self, table:str, id: int):
        with self.db as (conn, cursor):
            cursor.execute(f"""
                SELECT (details).key
                FROM {table}_statuses
                WHERE id = (
                    SELECT status
                    FROM "{table}"
                    WHERE id = {id}
                );
            """)
            status_key = cursor.fetchone()
        return status_key[0] if status_key else ""

    def _change_status(self, table, identifier, new_status, log=False):
        id = self.has(identifier)
        if not id:
            return self.logger.log(f"Error: Couldn't change status of {table} #{id}: Does not exist.", "") if log else ""

        new_status_id = self.has_status(new_status)
        if not new_status_id:
            return self.logger.log(f"Error: Couldn't change status of {table} #{id}: Status '{new_status}' is incorrect.", "") if log else ""

        current_status_id = self.has_status(self.status_of(identifier))[0]

        if new_status_id == current_status_id:
            return new_status

        with self.db as (conn, cursor):
            cursor.execute(
                f"""
                UPDATE "{table}"
                SET status = (
                    SELECT id
                    FROM "{table}_statuses"
                    WHERE (details).key = %s
                )
                WHERE id = %s
                """,
                (new_status, id),
            )
            conn.commit()

        log and self.logger.log(f"Info : Status of {table} #{id} has changed to '{new_status}'")
        return new_status

    def _all_getter(self, identifier_name, table_name):
        alls = {}

        with self.db as (conn, cursor):
            cursor.execute(f"""
            SELECT {identifier_name}
            FROM "{table_name}"
            """)
            all_identifiers = cursor.fetchall()

        for row in all_identifiers:
            obj_id = row[0]
            obj_info = self.get_info(obj_id)
            alls[obj_id] = obj_info

        return alls
    
    @abstractmethod
    def count(self, *args, **kwargs):
        pass

    @abstractmethod
    def has_status(self, *args, **kwargs):
        pass

    @abstractmethod
    def has(self, *args, **kwargs):
        pass

    @abstractmethod
    def status_of(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_info(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_all(self, *args, **kwargs):
        pass

    @abstractmethod
    def new(self, *args, **kwargs):
        pass

    @abstractmethod
    def change_status(self, *args, **kwargs):
        pass

    def clear_logs(self):
        self.logger.clear_logs()

    @multimethod
    def get_qr_info(self, qr_hex: str) -> dict:
        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT id, is_used, kit_id
                FROM "qr"
                WHERE unique_hex = %s
            """, (qr_hex,))
            result = cursor.fetchone()
        return {
            'id': int(result[0]),
            'is_used': bool(result[1]),
            'kit_id': int(result[2])
        } if result else {}
