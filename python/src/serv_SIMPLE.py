######### SERV
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, date
import time
import re
import traceback

from db_connection import *
from sys import stderr

from Logger import Logger
from colorama import Fore, Style


class MyServer(BaseHTTPRequestHandler):
    def _decide_request(self):
        # From narrowest to the broadest:
        patterns = [
            (r'^/(req)/([a-z]{16})/(-?\d+(\.\d+)?)&((-?\d+.\d+),(-?\d+.\d+))/$', "full"),
            (r'^/(req)/([a-z]{16})/$',                                           "qr"),
            (r'^/(req)/([a-z]{16})/',                                            "part"),
            (r'^/req/',                                                          "onlyheader"),
        ]
        for pattern, result in patterns:
            if re.match(pattern, self.path):
                return result
        return "rubbish"


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
            return True

        except Exception as e:
            logger.log(self, "server_error")
            self.send_response(500) # Internal Server Error (mb smthing is wrong with database)
            traceback.print_exc(file=stderr)
            print(Fore.RED + "\nInternal Server Error! Check database status or whatever...\n" + Style.RESET_ALL, file=stderr)
            return False


    def do_GET(self):
        logger = Logger("logs.log")
        request_type = self._decide_request()
        request = self.path[5:]
        qr = request[0:16]

        match request_type:
            case "full":
                if self._decide_qr(qr):
                    push_request(DB_LOGDATA, request)
                    self.send_response(200) # SAMPLE ACCEPTED
                    logger.log(self, "new_sample")
                    print(Fore.GREEN + "\nNew bio sample in collected_samples base!\n" + Style.RESET_ALL, file=stderr)
            case "qr":
                if self._decide_qr(qr):
                    self.send_response(202) # ACCEPTED
                    print(Fore.GREEN + "\nUnused QR code!\n" + Style.RESET_ALL, file=stderr)
                    logger.log(self, "valid_QR")
            case "part":
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
        self.end_headers()
