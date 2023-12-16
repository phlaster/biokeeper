######### SERV
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, date
import time
import re


######### DB
from db_settings import db
from sys import stderr
from sys import argv
import psycopg2

from add_research import connect2db
from db_settings import db

class Logger:
    def __init__(self, log_file):
        self.log_file = log_file

    def log(self, msg, is_request=False) -> None:
        with open(self.log_file, "a") as f:
            if is_request:
                ip = msg.client_address[0]
                path = msg.path[5:]
                print(datetime.now(), ip, path, file=f, sep=' ')
            else:
                print(msg, file=f)


def validate_request(path) -> bool:
    #           const     qr code     temp=int/float
    # Matching: /req/abc...16 chars...xyz/-15.0&30.1234000,60.1234000
    pattern = r'^/(req)/([a-z]{16})/(-?\d+(\.\d+)?)&((-?\d+.\d+),(-?\d+.\d+)$)'
    return re.match(pattern, path)


def in_db(qr) -> bool:
    connection, base = connect2db(db)
    base.execute(f"SELECT qrtest FROM sampl WHERE qrtest='{qr}'")
    x = base.fetchone()
    return x != None


def is_used(qr) -> bool:
    connection, base = connect2db(db)
    base.execute(f"SELECT id_samp FROM sampl WHERE qrtest='{qr}'") # FINDS sample ID from QRcode
    id_sample = int(base.fetchone()[0])
    base.execute(f"SELECT id_sample FROM data WHERE id_sample={id_sample}")
    x = base.fetchone()
    return x != None


def is_expired(qr) -> bool:
    connection, base = connect2db(db)
    base.execute(f"SELECT id_res FROM sampl WHERE qrtest='{qr}'") # FINDS sample ID from QRcode
    id_res = int(base.fetchone()[0])
    base.execute(f"SELECT data_start, data_end FROM reseach WHERE id_res={id_res}")
    date_end = base.fetchone()[1]
    return date_end < date.today()


def decide_qr(qr, handler) -> bool:
    try:
        if not in_db(qr):
            handler.send_response(422) # Unprocessable Content (no such qr code)
            print("\nIncorrect QR!\n", file=stderr)
            return False
        elif is_expired(qr):
            handler.send_response(406) # Not Acceptable (qrcode is expired)
            print("\nResearch expired!\n", file=stderr)
            return False
        elif is_used(qr):
            handler.send_response(410) # Gone (qrcode is used)
            print("\nQR is second-hand!\n", file=stderr)
            return False
        else:
            handler.send_response(200) # ALL GOOD
            return True
    except:
        handler.send_response(500) # Internal Server Error (mb smthing is wrong with DB)
        print("\nInternal Server Error! Check database status or whatever...\n", file=stderr)
        return False


def pushInfo(logdata, qr, content) -> None:
    try:
        connection, base = connect2db(logdata)
        base.execute(f"SELECT id_samp FROM sampl WHERE qrtest='{qr}'")
        id_sample = int(base.fetchone()[0])

        base.execute("""
                INSERT INTO data (id_sample, date, time, temperature, gps)
                VALUES (%s, %s, %s, %s, POINT(%s));
                """,
                (id_sample, date.today(), datetime.now(), int(float(content[0])), content[1])
            )
    finally:
        connection.commit()
        base.close()
        connection.close()


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        logger = Logger("logs.log")

        if validate_request(self.path):
            logger.log(self, True)
            request = self.path[5:]
            qr = request[0:16]

            if decide_qr(qr, self):
                if len(request) > len(qr)+1:
                    info = request[17:].split('&')
                    if len(info) != 2:
                        print("\nWrong data after correct qr_code!\n", file=stderr)

                    pushInfo(db, qr, info)
                    print("\nNew bio sample in data base!\n", file=stderr)
                    self.end_headers()
                else:
                    print("\nGood code, ready to get metadata!\n", file=stderr)
                    self.end_headers()
            else:
                self.end_headers()

        else:
            self.send_response(400) # BAD REQUEST
            self.end_headers()
            print("\nBad request!\n", file=stderr)
