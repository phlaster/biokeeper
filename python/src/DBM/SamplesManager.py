from DBM.ADBM import AbstractDBManager
from DBM.UsersManager import UsersManager
from DBM.KitsManager import KitsManager
from DBM.ResearchesManager import ResearchesManager

from multimethod import multimethod, Union
from geopy.geocoders import Nominatim
import concurrent.futures

import datetime

class SamplesManager(AbstractDBManager):
    def _get_closest_toponym(self, gps):
        geolocator = Nominatim(user_agent="Biokeeper")
        try:
            location = geolocator.reverse(f"{gps[0]}, {gps[1]}")
            return location.raw['display_name']
        except Exception as e:
            return str(gps)

    def _update_sample(self, identifier, column_name: str, value: Union[str, bytes], log=False):
        sample_id = self.has(identifier, log=log)
        if not sample_id:
            return self.logger.log(f"Error: Sample #{sample_id} does not exist.", 0) if log else 0
        with self.db as (conn, cursor):
            cursor.execute(f"""
                UPDATE "sample"
                SET {column_name} = %s
                WHERE id = %s
            """, (value, sample_id,))
            conn.commit()
        log and self.logger.log(f"Info : Sample #{sample_id} was updated at {column_name}.", sample_id)
        return sample_id

    def count(self, status:str="all"):
        return self._counter("sample_statuses", status)

    @multimethod
    def has_status(self, status: str):
        return self._is_status_of("sample", status)

    @multimethod
    def has(self, sample_id: int, log=False):
        id = self._SELECT("id", "sample", "id", sample_id)
        if not id:
            return self.logger.log(f"Error: No such sample #{sample_id}.", 0) if log else 0
        return id

    @multimethod
    def has(self, qr_unique_hex: str, log=False):
        qr_info = self.get_qr_info(qr_unique_hex)
        if not qr_info:
            return self.logger.log(f"Error: Wrong QR hex: '{qr_unique_hex}'", 0) if log else 0
        qr_id = qr_info["qr_id"]
        sample_id = self._SELECT("id", "sample", "qr_id", qr_id)
        if not sample_id:
            return self.logger.log(f"Error: No sample for QR #{qr_id}", 0) if log else 0

    @multimethod
    def status_of(self, sample_id: int, log=False):
        if not self.has(sample_id, log=log):
            return self.logger.log(f"Error: Sample #{sample_id} does not exist.", "") if log else ""
        return self._status_getter("sample", sample_id)

    @multimethod
    def get_info(self, identifier, log=False):
        sample_info_dict = {}
        sample_id = self.has(identifier, log=log)
        if not sample_id:
            return self.logger.log(f"Error: Sample #{sample_id} does not exist.", sample_info_dict) if log else sample_info_dict

        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT research_id, qr_id, owner_id, collected_at, created_at, updated_at, sent_to_lab_at, delivered_to_lab_at, gps, weather, comment, photo
                FROM "sample"
                WHERE id = %s
            """, (sample_id,))
            kit_data = cursor.fetchone()

            if kit_data:
                sample_info_dict['research_id'] = kit_data[0]
                sample_info_dict['qr_id'] = kit_data[1]
                sample_info_dict['status'] = self.status_of(sample_id)
                sample_info_dict['owner_id'] = kit_data[2]
                sample_info_dict['collected_at'] = kit_data[3].astimezone().isoformat()
                sample_info_dict['created_at'] = kit_data[4].astimezone().isoformat()
                sample_info_dict['updated_at'] = kit_data[5].astimezone().isoformat() 
                sample_info_dict['sent_to_lab_at'] = kit_data[6].astimezone().isoformat() if kit_data[6] else None
                sample_info_dict['delivered_to_lab_at'] = kit_data[7].astimezone().isoformat() if kit_data[7] else None
                sample_info_dict['gps'] = kit_data[8] #",".join(kit_data[8][1:-1].split(", "))
                sample_info_dict['weather'] = True if kit_data[9] else None
                sample_info_dict['comment'] = kit_data[10]
                sample_info_dict['photo'] = True if kit_data[11] else None
        return sample_info_dict

    
    def get_all(self):
        return self._all_getter("id", "sample")

    @multimethod
    def new(self,
        qr_unique_hex: str,
        research_name: str,
        collected_at: datetime.datetime,
        gps: tuple[float, float],
        log=False
    ):
        # Invoking necessary managers
        users = UsersManager(self.logdata, logfile=self.logfile)
        kits = KitsManager(self.logdata, logfile=self.logfile)
        researches = ResearchesManager(self.logdata, logfile=self.logfile)

        if (abs(gps[0]) > 90.0 or abs(gps[1]) > 180.0):
            return self.logger.log(f"Error: GPS coordinates {gps} are out of bounds.", 0) if log else 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Futures
            closest_toponym_future = executor.submit(self._get_closest_toponym, gps)
            research_info_future = executor.submit(researches.get_info, research_name)
            qr_info_future = executor.submit(self.get_qr_info, qr_unique_hex)

            if collected_at > datetime.datetime.now(datetime.timezone.utc) and log:
                self.logger.log(f"Warn : The sample seems to be collected in future at {collected_at}.")

            research_info = research_info_future.result() #researches.get_info(research_name)
            if not research_info:
                return self.logger.log(f"Error: Invalid research name '{research_name}'.", 0) if log else 0

            if research_info["status"] != "ongoing":
                return self.logger.log(f"Error: Research '{research_name}' is not in 'ongoing' status.", 0) if log else 0

            qr_info = qr_info_future.result() #self.get_qr_info(qr_unique_hex)
            if not qr_info:
                return self.logger.log(f"Error: No such QR in database.", 0) if log else 0
            
            qr_id = qr_info["id"]
            if qr_info["is_used"]:
                return self.logger.log(f"Error: QR #{qr_id} already 'is_used'.", 0) if log else 0
            
            kit_id = qr_info["kit_id"]
            if not kit_id:
                return self.logger.log(f"Error: QR code is not assigned to any kit.", 0) if log else 0

            kit_info = kits.get_info(kit_id)
            if not kit_info:
                return self.logger.log(f"Error: No #{kit_id} was found (very strange!).", 0) if log else 0
            
            kit_owner = kit_info["owner"]
            if not kit_owner:
                return self.logger.log(f"Error: Kit #{kit_id} has no owner.", 0) if log else 0

            if kit_info["status"] != "activated":
                return self.logger.log(f"Error: Kit associated with QR hasn't been activated.", 0) if log else 0

            owner_name = kit_owner["name"]
            kit_owner_status = users.status_of(owner_name)
            if kit_owner_status not in ['admin', 'volunteer']:
                return self.logger.log(f"Error: Owner of kit '{kit_owner}' is of status '{kit_owner_status}', which is not enough to publish samples.", False) if log else False
            
        
            research_id = research_info['id']
            owner_id = kit_owner["id"]
            
            closest_toponym = ', '.join(closest_toponym_future.result().split(", ")[:-4])
        with self.db as (conn, cursor):
            # Pushing the sample into the database
            cursor.execute("""
                INSERT INTO "sample"
                (research_id, owner_id, qr_id, collected_at, gps)
                VALUES (%s, %s, %s, %s, POINT(%s))
                RETURNING id
            """, (research_id, owner_id, qr_id, collected_at, str(gps)))
            sample_id = cursor.fetchone()[0]
            log and self.logger.log(f"""Info : For research #{research_id} user #{owner_id} collected a sample #{sample_id} near "{closest_toponym}".""")

            # Updating the QR code status
            cursor.execute("""
                UPDATE "qr"
                SET is_used = true
                WHERE id = %s
            """, (qr_id,))
            log and self.logger.log(f"Info : QR #{qr_id} is now 'is_used'")

            # Updating the personal counter of the user
            cursor.execute("""
                UPDATE "user"
                SET n_samples_collected = n_samples_collected + 1
                WHERE id = %s
                RETURNING n_samples_collected
            """, (owner_id,))
            new_personal_score = cursor.fetchone()[0]
            log and self.logger.log(f"Info : Personal counter of user '{owner_name}' is now {new_personal_score}")

            # Updating the research counter
            cursor.execute("""
                UPDATE "research"
                SET n_samples = n_samples + 1
                WHERE id = %s
                RETURNING n_samples
            """, (research_id,))
            n_samples_in_research = cursor.fetchone()[0]
            log and self.logger.log(f"Info : Counter of collected samples for '{research_name}' is now {n_samples_in_research}")

            conn.commit()

        return sample_id
    
    @multimethod
    def change_status(self, identifier, new_status: str, log=False):
        sample_id = self.has(identifier, log=log)
        if not sample_id:
            return self.logger.log(f"Error: No sample #{sample_id}", 0) if log else 0
        return self._change_status("sample", sample_id, new_status, log=log)
        
    @multimethod
    def push_weather(self, identifier, weather: str, log=False):
        sample_id = self.has(identifier, log=log)
        if not sample_id:
            return self.logger.log(f"Error: No sample #{sample_id}", 0) if log else 0
        return self._update_sample(sample_id, column_name="weather", value=weather, log=log)

    @multimethod
    def push_comment(self, identifier, comment: str, log=False):
        sample_id = self.has(identifier, log=log)
        if not sample_id:
            return self.logger.log(f"Error: No sample #{sample_id}", 0) if log else 0
        return self._update_sample(sample_id, column_name="comment", value=comment, log=log)
    
    @multimethod
    def push_photo(self, identifier, photo_bytes: bytes, log=False):
        sample_id = self.has(identifier, log=log)
        if not sample_id:
            return self.logger.log(f"Error: No sample #{sample_id}", 0) if log else 0
        return self._update_sample(sample_id, column_name="photo", value=photo_bytes, log=log)

    @multimethod
    def push_photo(self, identifier, photo_hex: str, log=False):
        sample_id = self.has(identifier, log=log)
        if not sample_id:
            return self.logger.log(f"Error: No sample #{sample_id}", 0) if log else 0
        photo_bytes = bytes.fromhex(photo_hex)
        return self._update_sample(sample_id, column_name="photo", value=photo_bytes, log=log)

    @multimethod
    def get_photo(self, identifier, log=False):
        sample_id = self.has(identifier, log=log)
        if not sample_id:
            return self.logger.log(f"Error: Sample #{sample_id} does not exist.", "") if log else ""
        photo = self._SELECT("photo", "sample", "id", sample_id)
        return photo if photo else b''

    def get_weather(self, identifier, log=False):
        sample_id = self.has(identifier, log=log)
        if not sample_id:
            return self.logger.log(f"Error: Sample #{sample_id} does not exist.", "") if log else ""
        weather = self._SELECT("weather", "sample", "id", sample_id)
        return weather if weather else ""