from DBM.ADBM import AbstractDBManager
from DBM.UsersManager import UsersManager
import os
from exceptions import NoKitException
from multimethod import multimethod
from utils import validate_return_from_db


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
        return validate_return_from_db({"kit": id},
                                       "kit_id",
                                       kit_id,
                                       self.logger if log else None,
                                       NoKitException)

    @multimethod
    def has(self, unique_hex: str, log=False):
        id = self._SELECT("id", "kit", "unique_hex", unique_hex)
        return validate_return_from_db({"kit": id},
                                       "unique_hex",
                                       unique_hex,
                                       self.logger if log else None,
                                       NoKitException)

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
                SELECT unique_hex, created_at, updated_at, status, owner_id, creator_id
                FROM "kit"
                WHERE id = %s
            """, (kit_id,))
            kit_data = cursor.fetchone()

            if kit_data:
                kit_info_dict['id'] = kit_id
                kit_info_dict['unique_hex'] = kit_data[0]
                kit_info_dict['created_at'] = kit_data[1].astimezone().isoformat()
                kit_info_dict['updated_at'] = kit_data[2].astimezone().isoformat()
                kit_info_dict['status'] = self.status_of(kit_id)
                kit_info_dict['creator_id'] = kit_data[5]
                kit_info_dict['owner_id'] = kit_data[4]
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
    def new(self, n_qrs: int, creator_id: int, log=False):
        kit_unique_hex = os.urandom(8).hex()
        qr_unique_hexes = self._generate_qr_bytes(n_qrs)

        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO "kit" (unique_hex, n_qrs, creator_id)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (kit_unique_hex, n_qrs, creator_id))
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


    def send_kit(self, kit_id: int, new_owner_id: int, log=False):
        with self.db as (conn, cursor):
            cursor.execute("""UPDATE "kit" SET owner_id = %s WHERE id = %s""", (new_owner_id, kit_id))
            conn.commit()
        with self.db as (conn, cursor):
            cursor.execute("""UPDATE "kit" SET status = 2 WHERE id = %s""", (kit_id,))
            conn.commit()
        log and self.logger.log(f"Info : Owner of Kit #{kit_id} changed to user #{new_owner_id}", kit_id)
        return kit_id

    def activate(self, kit_id: int, log=False):
        with self.db as (conn, cursor):
            cursor.execute("""UPDATE "kit" SET status = 3 WHERE id = %s""", (kit_id,))
            conn.commit()
        log and self.logger.log(f"Info : Kit #{kit_id} activated", kit_id)
        return kit_id
    

    def get_kits_by_user_identifier(self, user_identifier):
        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT id
                FROM "kit"
                WHERE owner_id = %s
            """, (user_identifier,))
            kits = cursor.fetchall()
            if kits:
                kits = kits[0]
            else:
                kits = []
            kits = [{'kit_id': kit_id} for kit_id in kits]
        return kits
    
    def get_created_kits_by_user_identifier(self, user_identifier):

        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT k.id, k.n_qrs, k.unique_hex, k.created_at, k.owner_id, u.name as owner_name
                FROM "kit" k
                LEFT JOIN "user" u ON k.owner_id = u.id
                WHERE k.creator_id = %s
            """, (user_identifier,))
            kits = cursor.fetchall()

            if kits:
                kits = [{'id': kit[0], 'n_qrs': kit[1], 'unique_hex': kit[2], 'created_at': kit[3], 'owner_id': kit[4], 'owner_name': kit[5]} for kit in kits]
            else:
                kits = []
        return kits