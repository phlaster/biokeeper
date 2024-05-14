from DBM.ADBM import AbstractDBManager
from DBM.UsersManager import UsersManager
from DBM.KitsManager import KitsManager
from DBM.ResearchesManager import ResearchesManager

import datetime

class SamplesManager(AbstractDBManager):
    def count(self, status:str="all"):
        """
        Returns number of researches with different statuses.
        'all' for all statuses OR
        Currently possible statuses: "collected", "sent", "delivered"
        """
        return self._counter("sample_statuses", status)

    
    def has_status(self, status):
        return self._is_status_of("sample", status)

    
    def has(self, sample_id):
        return self._is("sample_id", "samples", "sample_id", sample_id)

    
    def status_of(self, sample_id):
        """
        -- logging --
        Returns the status of a kit with the given sample_id.
        If the kit does not exist, returns False.
        """
        if not self.has(sample_id):
            self.logger.log_message(f"Error: Sample #{sample_id} does not exist.")
            return ""
        return self._status_getter("sample_status", "samples", "sample_id", "sample_statuses", sample_id)


    def get_info(self, sample_id: int):
        """
        -- logging --
        Returns a dictionary containing kit information for the kit with the given kit_id.
        If the kit does not exist, returns empty dict.
        """
        sample_info_dict = {}
        if not self.has(sample_id):
            self.logger.log_message(f"Error: Sample #{sample_id} does not exist.")
            return sample_info_dict

        with self.db as (conn, cursor):
            cursor.execute("SELECT research_id, qr_id, collected_at, uploaded_at, sent_to_lab_at, delivered_to_lab_at, sample_status, gps, weather_conditions, user_comment FROM samples WHERE sample_id = %s", (sample_id,))
            kit_data = cursor.fetchone()

            if kit_data:
                sample_info_dict['research_id'] = kit_data[0]
                sample_info_dict['qr_id'] = kit_data[1]
                sample_info_dict['collected_at'] = kit_data[2].strftime("%Y-%m-%d, %H:%M:%S") if kit_data[2] else None
                sample_info_dict['uploaded_at'] = kit_data[3].strftime("%Y-%m-%d, %H:%M:%S") 
                sample_info_dict['sent_to_lab_at'] = kit_data[4].strftime("%Y-%m-%d, %H:%M:%S") if kit_data[4] else None
                sample_info_dict['delivered_to_lab_at'] = kit_data[5].strftime("%Y-%m-%d, %H:%M:%S") if kit_data[5] else None

                cursor.execute("SELECT status_key FROM sample_statuses WHERE status_id = %s", (kit_data[6],))
                kit_status_key = cursor.fetchone()[0]
                sample_info_dict['sample_status'] = kit_status_key
                sample_info_dict['gps'] = kit_data[7]
                sample_info_dict['weather_conditions'] = kit_data[8]
                sample_info_dict['user_comment'] = kit_data[9]
        return sample_info_dict

    
    def get_all(self):
        return self._all_getter("sample_id", "samples")

    
    def new(self,
        qr_bytes: bytes,
        research_name: str,
        collected_at: datetime.datetime,
        gps: tuple[float, float],
        weather: str = None,
        user_comment: str = None,
        photo: bytes = None
    ):
        """
        -- logging --
        Returns sample_id if successfull
        Inserts a new sample into the database with the provided information.
        Checks if the research is ongoing, the QR code is valid and not used, the kit is activated, and the user is a volunteer.
        Increments the n_samples_collected of the user by 1 if all conditions are met.
        """
        # Invoking necessary managers
        users = UsersManager(self.logdata, logfile=self.logfile)
        kits = KitsManager(self.logdata, logfile=self.logfile)
        researches = ResearchesManager(self.logdata, logfile=self.logfile)

        if collected_at > datetime.datetime.now():
            self.logger.log_message(f"Warn : The sample seems to be collected in future at {collected_at}.")

        research_info = researches.get_info(research_name)
        if not research_info:
            self.logger.log_message(f"Error: Invalid research name '{research_name}'.")
            return False

        if research_info["research_status"] != "ongoing":
            self.logger.log_message(f"Error: Research '{research_name}' is not in 'ongoing' status.")
            return False

        qr_info = self.get_qr_info(qr_bytes)
        if not qr_info:
            self.logger.log_message(f"Error: No such QR in database.")
            return False
        
        qr_id = qr_info["qr_id"]
        if qr_info["is_used"]:
            self.logger.log_message(f"Error: QR #{qr_id} already 'is_used'.")
            return False
        
        kit_id = qr_info["kit_id"]
        if not kit_id:
            self.logger.log_message(f"Error: QR code is not assigned to any kit.")
            return False

        kit_info = kits.get_info(kit_id)
        if not kit_info:
            self.logger.log_message(f"Error: No #{kit_id} was found (very strange!).")
            return False
        
        kit_owner = kit_info["owner"]
        if not kit_owner:
            self.logger.log_message(f"Error: Kit #{kit_id} has no owner.")
            return False

        if kit_info["kit_status"] != "activated":
            self.logger.log_message(f"Error: Kit associated with QR hasn't been activated.")
            return False

        kit_owner_status = users.status_of(kit_owner["user_name"])
        if kit_owner_status not in ['admin', 'volunteer']:
            self.logger.log_message(f"Error: Owner of kit '{kit_owner}' is of status '{kit_owner_status}', which is not enough to publish samples.")
            return False
        
        with self.db as (conn, cursor):
            cursor.execute("""
                INSERT INTO samples (research_id, qr_id, collected_at, gps, weather_conditions, user_comment, photo)
                VALUES (%s, %s, %s, POINT(%s), %s, %s, %s)
                RETURNING sample_id
            """, (research_info['research_id'], qr_id, collected_at, str(gps), weather, user_comment, photo))
            sample_id = cursor.fetchone()[0]
            cursor.execute("UPDATE sample_statuses SET n = n + 1 WHERE status_id = 1")
            cursor.execute("UPDATE qrs SET is_used = true WHERE qr_id = %s", (qr_id,))
            self.logger.log_message(f"Info : QR #{qr_id} is now 'is_used'")
            cursor.execute("UPDATE users SET n_samples_collected = n_samples_collected + 1 WHERE user_id = %s RETURNING n_samples_collected", (kit_owner["user_id"],))
            new_personal_score = cursor.fetchone()[0]
            self.logger.log_message(f"Info : Personal counter of user '{kit_owner['user_name']}' is now {new_personal_score}")
            conn.commit()

        self.logger.log_message("Info : New sample inserted successfully.")
        return sample_id

    
    def change_status(self, sample_id, new_status):
        return self._change_status("sample_id", "samples", "sample_status", "sample_statuses", sample_id, new_status)

    
    def change_sample_details(self, sample_id: int, weather: str = None, user_comment: str = None, photo: bytes = None):
        """
        -- logging --
        Updates the weather conditions, user comment, and photo of an existing sample in the database.
        Returns True if the update is successful, False otherwise.
        """
        if weather == user_comment == photo == None:
            return False

        with self.db as (conn, cursor):
            cursor.execute("SELECT * FROM samples WHERE sample_id = %s", (sample_id,))
            sample_data = cursor.fetchone()
            if not sample_data:
                self.logger.log_message(f"Error: Sample #{sample_id} does not exist.")
                return False

            logmsg = []
            update_query = "UPDATE samples SET "
            update_values = []

            if weather is not None:
                update_query += "weather_conditions = %s, "
                update_values.append(weather)
                logmsg.append("weather info")

            if user_comment is not None:
                update_query += "user_comment = %s, "
                update_values.append(user_comment)
                logmsg.append("user comment")

            if photo is not None:
                update_query += "photo = %s, "
                update_values.append(photo)
                logmsg.append("photo")

            # Remove the trailing comma and space
            update_query = update_query[:-2]

            update_query += " WHERE sample_id = %s"
            update_values.append(sample_id)

            cursor.execute(update_query, update_values)
            conn.commit()
            self.logger.log_message(f"Info : Pushed details: {', '.join(logmsg)} for sample #{sample_id}.")
        return True

    def get_photo(self, sample_id):
        if not self.has(sample_id):
            self.logger.log_message(f"Error: Sample #{sample_id} does not exist.")
            return b''

        with self.db as (conn, cursor):
            cursor.execute("SELECT photo FROM samples WHERE sample_id = %s", (sample_id,))
            photo = cursor.fetchone()[0]
        
        return photo if photo else b''

