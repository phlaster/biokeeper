######### SERV
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, date
import time


######### DB
from settings.db_settings import db
from sys import stderr
from sys import argv
import psycopg2

from add_research import connect2db
from settings.db_settings import db, real_host



hostName = "0.0.0.0"
serverPort = 8080


def isrequest(path):
    return path.startswith('/req/')

def log_correct_request(msg):
    with open("logs.log", "a") as log:
        ip = msg.client_address[0]
        request = msg.path[5:]
        print(datetime.now(), ip, request, file=log, sep=' ')

def in_db(qr):
    connection, base = connect2db(db)
    base.execute(f"SELECT qrtest FROM sampl WHERE qrtest='{qr}'")
    x = base.fetchone()
    return x != None

def is_used(qr):
    connection, base = connect2db(db)
    base.execute(f"SELECT id_samp FROM sampl WHERE qrtest='{qr}'") # FINDS sample ID from QRcode
    id_sample = int(base.fetchone()[0])
    base.execute(f"SELECT id_sample FROM data WHERE id_sample={id_sample}")
    x = base.fetchone()
    return x != None

def is_expired(qr):
    connection, base = connect2db(db)
    base.execute(f"SELECT id_res FROM sampl WHERE qrtest='{qr}'") # FINDS sample ID from QRcode
    id_res = int(base.fetchone()[0])
    base.execute(f"SELECT data_start, data_end FROM reseach WHERE id_res={id_res}")
    date_end = base.fetchone()[1]
    return date_end < date.today()

def decide_qr(qr, handler):
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

def pushInfo(logdata, qr, content):
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
        if isrequest(self.path):
            log_correct_request(self)
            # print("Path: ",self.path)
            request = self.path[5:]
            # print("Request: ", request)
            # print("Length of request: ", len(request))
            qr = request[0:16]
            # print("QR: ", qr)

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



if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (real_host, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        webServer.server_close()
        print("Server stopped.")