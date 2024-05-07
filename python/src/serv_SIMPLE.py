######### SERV
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, date
import time
import re
import traceback


######### DB
from db_connection import *
from sys import stderr

from Logger import Logger
from colorama import Fore, Style

DB_LOGDATA = DB_from_docker if is_docker() else DB


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
                print(Fore.LIGHTRED_EX + "\nIncorrect QR!\n" + Style.RESET_ALL, file=stderr)
                return False
            elif is_expired(DB_LOGDATA, qr):
                self.send_response(406) # Not Acceptable (qrcode is expired)
                logger.log(self, "expired_research")
                print(Fore.LIGHTRED_EX + "\nResearch expired!\n" + Style.RESET_ALL, file=stderr)
                return False
            elif is_used(DB_LOGDATA, qr):
                self.send_response(410) # Gone (qrcode is used)
                logger.log(self, "used_qr")
                print(Fore.LIGHTRED_EX + "\nQR is second-hand!\n" + Style.RESET_ALL, file=stderr)
                return False
            else:
                return True

        except Exception as e:
            print(Fore.RED + "\nInternal Server Error! Check database status or whatever...\n" + Style.RESET_ALL, file=stderr)
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
                    print(Fore.GREEN + "\nNew bio sample in collected_samples base!\n" + Style.RESET_ALL, file=stderr)

            case "qr":
                request = self.path[5:]
                qr = request[0:16]
                if self._decide_qr(qr):
                    self.send_response(202) # ACCEPTED
                    print(Fore.GREEN + "\nUnused QR code!\n" + Style.RESET_ALL, file=stderr)
                    logger.log(self, "valid_QR")

            case "part":
                request = self.path[5:]
                qr = request[0:16]
                if self._decide_qr(qr):
                    self.send_response(206) # PARTIAL CONTENT
                    print(Fore.GREEN + "\nUnused QR code with incomplete request!\n" + Style.RESET_ALL, file=stderr)
                    logger.log(self, "valid_QR_incomplete_request")

            case "onlyheader":
                logger.log(self, "only_header")
                self.send_response(415) # Unsupported Media Type
                print(Fore.MAGENTA + "\nNonsence after correct header!\n" + Style.RESET_ALL, file=stderr)

            case "rubbish":
                self.send_response(412) # Precondition Failed
                print(Fore.MAGENTA + "\nWrong request header!\n" + Style.RESET_ALL, file=stderr)

            case _:
                pass

        self.end_headers()
