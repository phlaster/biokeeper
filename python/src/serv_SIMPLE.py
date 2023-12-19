######### SERV
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, date
import time
import re
import traceback


######### DB
from db_connection import DB, DB_from_docker, is_docker, connect2db
from sys import stderr
from sys import argv
import psycopg2

from Logger import Logger


DB_LOGDATA = DB_from_docker if is_docker() else DB

def in_db(db_logdata, qr) -> bool:
    try:
        connection, cursor = connect2db(db_logdata)
        cursor.execute(f"SELECT qr_text FROM generated_qrs WHERE qr_text='{qr}'")
        x = cursor.fetchone()
        return x != None
    finally:
        cursor.close()
        connection.close()


def is_used(db_logdata, qr) -> bool:
    try:
        connection, cursor = connect2db(db_logdata)
        cursor.execute(f"SELECT qr_id FROM generated_qrs WHERE qr_text='{qr}'") # FINDS QR ID for given QR string
        qr_id = int(cursor.fetchone()[0])

        cursor.execute(f"SELECT qr_id FROM collected_samples WHERE qr_id={qr_id}")
        x = cursor.fetchone()
        return x != None
    finally:
        cursor.close()
        connection.close()


def is_expired(db_logdata, qr) -> bool:
    try:
        connection, cursor = connect2db(db_logdata)
        cursor.execute(f"SELECT research_id FROM generated_qrs WHERE qr_text='{qr}'") # FINDS sample ID from QRcode
        research_id = int(cursor.fetchone()[0])
        cursor.execute(f"SELECT day_start, day_end FROM researches WHERE research_id={research_id}")
        date_end = cursor.fetchone()[1]
        return date_end < date.today()
    finally:
        cursor.close()
        connection.close()


def push_request(db_logdata, request) -> None:
    qr = request[0:16]
    req_body = request[17:].split('&')
    temperature = round(float(req_body[0]))
    location = req_body[1].strip('/')

    try:
        connection, cursor = connect2db(db_logdata)
        cursor.execute(f"SELECT qr_id FROM generated_qrs WHERE qr_text='{qr}'")
        qr_id = int(cursor.fetchone()[0])

        cursor.execute("""
            INSERT INTO collected_samples (qr_id, date, time, temperature, gps)
            VALUES (%s, %s, %s, %s, POINT(%s));
            """,
            (qr_id, date.today(), datetime.now(), temperature, location)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


class MyServer(BaseHTTPRequestHandler):
    def _decide_request(self):
        if self._fully_valid():
            return "full"
        if self._qr_only():
            return "qr"
        elif self._partially_valid():
            return "part"
        elif self.path.startswith("/req/"):
            return "onlyheader"
        else:
            return "rubbish"


    def _fully_valid(self) -> bool:
        #           const     qr code     temp=int/float
        # Matching: /req/abc...16 chars...xyz/-15.0&30.1234000,60.1234000
        pattern = r'^/(req)/([a-z]{16})/(-?\d+(\.\d+)?)&((-?\d+.\d+),(-?\d+.\d+))/$'
        return re.match(pattern, self.path)

    def _qr_only(self) -> bool:
        pattern = r'^/(req)/([a-z]{16})/$' # [...]
        return re.match(pattern, self.path)

    def _partially_valid(self) -> bool:
        pattern = r'^/(req)/([a-z]{16})/' # [...)
        return re.match(pattern, self.path)



    def _decide_qr(self, qr) -> bool:
        logger = Logger("logs.log")
        try:
            if not in_db(DB_LOGDATA, qr):
                self.send_response(422) # Unprocessable Content (no such qr code)
                logger.log(self, "QR_not_in_DB")
                print("\nIncorrect QR!\n", file=stderr)
                return False
            elif is_expired(DB_LOGDATA, qr):
                self.send_response(406) # Not Acceptable (qrcode is expired)
                logger.log(self, "expired_research")
                print("\nResearch expired!\n", file=stderr)
                return False
            elif is_used(DB_LOGDATA, qr):
                self.send_response(410) # Gone (qrcode is used)
                logger.log(self, "used_qr")
                print("\nQR is second-hand!\n", file=stderr)
                return False
            else:
                return True

        except Exception as e:
            print("\nInternal Server Error! Check database status or whatever...\n", file=stderr)
            logger.log(self, "server_error")
            traceback.print_exc(file=stderr)
            self.send_response(500) # Internal Server Error (mb smthing is wrong with DB)
            return False


    def do_GET(self):
        logger = Logger("logs.log")
        request_type = self._decide_request()

        match request_type:
            case "full":
                request = self.path[5:]
                qr = request[0:16]

                if self._decide_qr(qr):
                    push_request(DB_LOGDATA, request)
                    self.send_response(200) # SAMPLE ACCEPTED
                    logger.log(self, "new_sample")
                    print("\nNew bio sample in collected_samples base!\n", file=stderr)

            case "qr":
                request = self.path[5:]
                qr = request[0:16]
                if self._decide_qr(qr):
                    self.send_response(202) # ACCEPTED
                    print("\nUnused QR code!\n", file=stderr)
                    logger.log(self, "valid_QR")

            case "part":
                request = self.path[5:]
                qr = request[0:16]
                if self._decide_qr(qr):
                    self.send_response(206) # PARTIAL CONTENT
                    print("\nUnused QR code with incomplete request!\n", file=stderr)
                    logger.log(self, "valid_QR_incomplete_request")

            case "onlyheader":
                logger.log(self, "only_header")
                self.send_response(415) # Unsupported Media Type
                print("\nNonsence after correct header!\n", file=stderr)

            case "rubbish":
                self.send_response(412) # Precondition Failed
                print("\nWrong request header!\n", file=stderr)

            case _:
                pass

        self.end_headers()
