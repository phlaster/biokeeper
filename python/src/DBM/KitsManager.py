from ADBM import AbstractDBManager
from UsersManager import UsersManager
import os

class KitsManager(AbstractDBManager):
    def _generate_qr_bytes(self, n: int, l: int):
        return [os.urandom(l) for _ in range(n)]



    def count(self, status):
        """
        Returns number of kits with different statuses.
        'all' for all statuses OR
        Currently possible statuses: "created", "sent", "activated"
        """
        return self._counter("kit_statuses", status)

    
    def has_status(self, status):
        return self._is_status_of("kit", status)

    
    def has(self, kit_id):
        return self._is("kit_id", "kits", "kit_id", kit_id)

    
    def status_of(self, kit_id):
        """
        -- logging --
        Returns the status of a kit with the given kit_id.
        If the kit does not exist, returns False.
        """
        if not self.has(kit_id):
            self.logger.log_message(f"Error: Kit #{kit_id} does not exist.")
            return ""
        return self._status_getter("kit_status", "kits", "kit_id", "kit_statuses", kit_id)

    
    def get_qrs(self, kit_id: int):
        """
        -- logging --
        Returns a list of tuples containing (qr_id, qr_unique_code) for the kit with the given kit_id.
        If the kit does not exist, returns empty dict.
        """
        qr_info = {}
        if not self.has(kit_id):
            self.logger.log_message(f"Error: Kit #{kit_id} does not exist.")
            return qr_info


        with self.db as (conn, cursor):
            cursor.execute("SELECT qr_id, qr_unique_code FROM qrs WHERE kit_id = %s", (kit_id,))
            qr_info_tuples = cursor.fetchall()

        for qr_id, qr_unique_code in qr_info_tuples:
            qr_info[qr_id] = bytes(qr_unique_code)

        return qr_info

    
    def get_info(self, kit_id: int):
        """
        -- logging --
        Returns a dictionary containing kit information for the kit with the given kit_id.
        If the kit does not exist, returns empty dict.
        """
        kit_info_dict = {}
        if not self.has(kit_id):
            self.logger.log_message(f"Error: Kit #{kit_id} does not exist.")
            return kit_info_dict

        with self.db as (conn, cursor):
            cursor.execute("SELECT kit_unique_code, created_at, updated_at, kit_status, user_id FROM kits WHERE kit_id = %s", (kit_id,))
            kit_data = cursor.fetchone()

            if kit_data:
                kit_info_dict['kit_unique_code'] = bytes(kit_data[0])
                kit_info_dict['created_at'] = kit_data[1]
                kit_info_dict['updated_at'] = kit_data[2]

                cursor.execute("SELECT status_key FROM kit_statuses WHERE status_id = %s", (kit_data[3],))
                kit_status_key = cursor.fetchone()[0]
                kit_info_dict['kit_status'] = kit_status_key

                if kit_data[4]:  # Check if user_id is not None
                    cursor.execute("SELECT user_id, user_name FROM users WHERE user_id = %s", (kit_data[4],))
                    owner_data = cursor.fetchone()
                    owner_dict = {'user_id': owner_data[0], 'user_name': owner_data[1]} if owner_data else None
                    kit_info_dict['owner'] = owner_dict
                else:
                    kit_info_dict['owner'] = None

                kit_info_dict['qrs'] = self.get_qrs(kit_id)

        return kit_info_dict

    
    def get_all(self):
        return self._all_getter(self, "kit_id", "kits")

    
    def new(self, n_qrs: int):
        """
        -- logging --
        Inserts a new kit with `n_qrs` QRs into the database.
        Returns the kit_id if successful, otherwise False.
        """
        kit_unique_code = os.urandom(16)
        qr_unique_codes = self._generate_qr_bytes(n_qrs, 10)
        
        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO kits (kit_unique_code, n_qrs, kit_status)
                VALUES (%s, %s, 1)
                RETURNING kit_id
            """, (kit_unique_code, n_qrs))
            kit_id = cursor.fetchone()[0]
            cursor.execute("UPDATE kit_statuses SET n = n + 1 WHERE status_id = 1")
            for qr_unique_code in qr_unique_codes:
                cursor.execute("""
                    INSERT INTO qrs (qr_unique_code, kit_id)
                    VALUES (%s, %s)
                """, (qr_unique_code, kit_id))
            conn.commit()
        self.logger.log_message(f"Info : Kit #{kit_id} with {n_qrs} QRs has been created")
        return kit_id

    
    def change_status(self, kit_id, new_status):
        return self._change_status("kit_id", "kits", "kit_status", "kit_statuses", kit_id, new_status)

    
    def change_owner(self, kit_id: int, user_name: str):
        """
        -- logging --
        Changes the owner of a kit with the given kit_id to the user with the specified user_name.
        Returns kit_id if successful, otherwise False.
        """
        if not self.has(kit_id):
            self.logger.log_message(f"Error: Kit #{kit_id} does not exist.")
            return False

        users = UsersManager(self.logdata, logfile=self.logfile)
        user_id = users.has(user_name)
        if not user_id:
            self.logger.log_message(f"Error: User '{user_name}' does not exist.")
            return False

        with self.db as (conn, cursor):
            cursor.execute("UPDATE kits SET user_id = %s WHERE kit_id = %s", (user_id, kit_id))
            conn.commit()

        self.logger.log_message(f"Info : Owner of Kit #{kit_id} changed to '{user_name}'")
        return kit_id