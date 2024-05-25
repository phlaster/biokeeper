from DBM.ADBM import AbstractDBManager
from DBM.UsersManager import UsersManager
import os
from multimethod import multimethod

class KitsManager(AbstractDBManager):
    def _generate_qr_bytes(self, n: int, l: int = 10):
        return [os.urandom(l).hex() for _ in range(n)]

    @multimethod
    def count(self, status: str = "all"):
        return self._counter("kit_statuses", status)

    @multimethod
    def has_status(self, status: str):
        return self._is_status_of("kit", status)

    @multimethod
    def has(self, kit_id: int, log=False):
        id = self._SELECT("id", "kit", "id", kit_id)
        if not id:
            return self.logger.log(f"Error: No kit #{kit_id}.", 0) if log else 0
        return id

    @multimethod
    def has(self, unique_hex: str, log=False):
        id = self._SELECT("id", "kit", "unique_hex", unique_hex)
        if not id:
            return self.logger.log(f"Error: No kit with hex '{unique_hex}'.", 0) if log else 0
        return id

    def status_of(self, identifier, log=False):
        kit_id = self.has(identifier)
        if not id:
            return self.logger.log(f"Error: Kit #{kit_id} does not exist.", "") if log else ""
        return self._status_getter("kit", kit_id)

    def get_qrs(self, identifier, log=False):
        qr_info = {}
        kit_id = self.has(identifier)
        if not kit_id:
            return self.logger.log(f"Error: Kit #{kit_id} does not exist.", qr_info) if log else qr_info

        with self.db as (conn, cursor):
            cursor.execute(
                """SELECT id, unique_hex FROM "qr" WHERE kit_id = %s""", (kit_id,))
            qr_info_tuples = cursor.fetchall()

        for qr_id, qr_hex in qr_info_tuples:
            qr_info[qr_id] = qr_hex

        return qr_info

    def get_info(self, identifier, log=False):
        kit_info_dict = {}
        kit_id = self.has(identifier)
        if not kit_id:
            return self.logger.log(f"Error: Kit #{kit_id} does not exist.", kit_info_dict) if log else kit_info_dict

        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT unique_hex, created_at, updated_at, status, owner_id
                FROM "kit"
                WHERE id = %s
            """, (kit_id,))
            kit_data = cursor.fetchone()

            if kit_data:
                kit_info_dict['unique_hex'] = kit_data[0]
                kit_info_dict['created_at'] = kit_data[1].astimezone().isoformat()
                kit_info_dict['updated_at'] = kit_data[2].astimezone().isoformat()
                kit_info_dict['status'] = self.status_of(kit_id)

                if kit_data[4]:  # Check if user_id is not None
                    cursor.execute("""
                        SELECT id, name
                        FROM "user"
                        WHERE id = %s
                    """, (kit_data[4],))
                    owner_data = cursor.fetchone()
                    owner_dict = {
                        'id': owner_data[0],
                        'name': owner_data[1]
                    } if owner_data else None
                    kit_info_dict['owner'] = owner_dict
                else:
                    kit_info_dict['owner'] = None
                kit_info_dict['qrs'] = self.get_qrs(kit_id)
        return kit_info_dict

    
    def get_all(self):
        return self._all_getter("id", "kit")

    @multimethod
    def new(self, n_qrs: int, log=False):
        if n_qrs > 50:
            self.logger.log(f"Info : No more than 50 QRs in one kit!")
            n_qrs = 50
        kit_unique_hex = os.urandom(8).hex()
        qr_unique_hexes = self._generate_qr_bytes(n_qrs)
        
        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO "kit" (unique_hex, n_qrs)
                VALUES (%s, %s)
                RETURNING id
            """, (kit_unique_hex, n_qrs))
            kit_id = cursor.fetchone()[0]
            for qr_unique_code in qr_unique_hexes:
                cursor.execute("""
                    INSERT INTO "qr" (unique_hex, kit_id)
                    VALUES (%s, %s)
                """, (qr_unique_code, kit_id))
            conn.commit()
        log and self.logger.log(f"Info : Kit #{kit_id} with {n_qrs} QRs has been created", kit_id)
        return kit_id

    
    def change_status(self, identifier, new_status, log=False):
        return self._change_status("kit", identifier, new_status, log=log)

    
    def change_owner(self, identifier, new_owner_identifier, log=False):
        kit_id = self.has(identifier, log=log)
        if not kit_id:
            return self.logger.log(f"Error: Kit #{kit_id} does not exist.", False) if log else False

        users = UsersManager(self.logdata, logfile=self.logfile)
        user_id = users.has(new_owner_identifier, log=log)
        if not user_id:
            return self.logger.log(f"Error: User #{user_id} does not exist.", False) if log else False

        with self.db as (conn, cursor):
            cursor.execute("""UPDATE "kit" SET owner_id = %s WHERE id = %s""", (user_id, kit_id))
            conn.commit()
        log and self.logger.log(f"Info : Owner of Kit #{kit_id} changed to user #{user_id}", kit_id)
        return kit_id
