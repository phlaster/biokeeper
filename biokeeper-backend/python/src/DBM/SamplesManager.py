from DBM.ADBM import AbstractDBManager
from DBM.UsersManager import UsersManager
from DBM.KitsManager import KitsManager
from DBM.ResearchesManager import ResearchesManager

from schemas.samples import GpsModel

from utils import get_closest_toponym 
from multimethod import multimethod, Union
import concurrent.futures
from exceptions import NoSampleException, NoQrCodeException
import datetime
from utils import validate_return_from_db

class SamplesManager(AbstractDBManager):

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
        return validate_return_from_db({"sample": id},
                                       "sample_id",
                                       sample_id,
                                       self.logger if log else None,
                                       NoSampleException)

    @multimethod
    def has(self, qr_unique_hex: str, log=False):
        qr_info = self.get_qr_info(qr_unique_hex)
        qr_info=validate_return_from_db(
            {"qr_info": qr_info},
            "qr_unique_hex",
            qr_unique_hex,
            self.logger if log else None,
            NoQrCodeException
        )
        qr_id = qr_info["qr_id"]
        sample_id = self._SELECT("id", "sample", "qr_id", qr_id)
        return validate_return_from_db({"sample": sample_id},
                                       "qr_id",
                                       qr_id,
                                       self.logger if log else None,
                                       NoSampleException
                                       )

    @multimethod
    def status_of(self, sample_id: int, log=False):
        if not self.has(sample_id, log=log):
            return self.logger.log(f"Error: Sample #{sample_id} does not exist.", "") if log else ""
        return self._status_getter("sample", sample_id)

    @multimethod
    def get_info(self, sample_id: int, log=False):
        sample_info_dict = {}
        sample_id = self.has(sample_id, log=log)
        if not sample_id:
            return self.logger.log(f"Error: Sample #{sample_id} does not exist.", sample_info_dict) if log else sample_info_dict

        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT research_id, qr_id, owner_id, collected_at, created_at, updated_at, sent_to_lab_at, delivered_to_lab_at, gps, weather, comment, photo
                FROM "sample"
                WHERE id = %s
            """, (sample_id,))
            sample_data = cursor.fetchone()

            if sample_data:
                sample_info_dict['id'] = sample_id 
                sample_info_dict['research_id'] = sample_data[0]
                sample_info_dict['qr_id'] = sample_data[1]
                sample_info_dict['status'] = self.status_of(sample_id)
                sample_info_dict['owner_id'] = sample_data[2]
                sample_info_dict['collected_at'] = sample_data[3].astimezone().isoformat()
                sample_info_dict['created_at'] = sample_data[4].astimezone().isoformat()
                sample_info_dict['updated_at'] = sample_data[5].astimezone().isoformat() 
                sample_info_dict['sent_to_lab_at'] = sample_data[6].astimezone().isoformat() if sample_data[6] else None
                sample_info_dict['delivered_to_lab_at'] = sample_data[7].astimezone().isoformat() if sample_data[7] else None
                sample_info_dict['gps'] = sample_data[8] #",".join(sample_data[8][1:-1].split(", "))
                sample_info_dict['weather'] = True if sample_data[9] else None
                sample_info_dict['comment'] = sample_data[10]
                sample_info_dict['photo'] = True if sample_data[11] else None
        return sample_info_dict

    
    def get_all(self):
        return self._all_getter("id", "sample")

    def new(self,
        qr_id: int,
        research_id: int,
        owner_id: int,
        collected_at: datetime.datetime,
        gps: GpsModel,
        weather: str | None = None,
        user_comment: str | None = None,
        photo_hex_string: str | None = None,
        log: bool = False
    ):
        gps_string = f"{gps.latitude},{gps.longitude}"
        
        closest_toponym = ', '.join(get_closest_toponym(gps.latitude, gps.longitude).split(",")[:-4])

        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO "sample"
                (research_id, owner_id, qr_id, collected_at, gps, weather, comment)
                VALUES (%s, %s, %s, %s, POINT(%s), %s, %s)
                RETURNING id
            """, (research_id, owner_id, qr_id, collected_at, gps_string, weather, user_comment)
            )
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
            log and self.logger.log(f"Info : Personal counter of user with id '{owner_id}' is now {new_personal_score}")

            # Updating the research counter
            cursor.execute("""
                UPDATE "research"
                SET n_samples = n_samples + 1
                WHERE id = %s
                RETURNING n_samples
            """, (research_id,))

            n_samples_in_research = cursor.fetchone()[0]
            log and self.logger.log(f"Info : Counter of collected samples for research with id '{research_id}' is now {n_samples_in_research}")

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

    def get_samples_by_user_identifier(self, user_identifier):
        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT id
                FROM "sample"
                WHERE owner_id = %s
            """, (user_identifier,))
            samples = cursor.fetchall()
            if samples:
                samples = samples[0]
            else:
                samples = []
            samples = [{'sample_id': sample_id} for sample_id in samples]
        return samples