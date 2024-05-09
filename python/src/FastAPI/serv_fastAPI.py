from fastapi import FastAPI, HTTPException, Response, status
from db_connection import *
import re
import traceback

from Logger import Logger
from colorama import Fore, Style

app = FastAPI()

logger = Logger("logs.log")

def decide_request(path: str):
    patterns = [
        (r'^/(req)/([a-z]{16})/(-?\d+(\.\d+)?)&((-?\d+.\d+),(-?\d+.\d+))/$', "full"),
        (r'^/(req)/([a-z]{16})/$',                                           "qr"),
        (r'^/(req)/([a-z]{16})/',                                            "part"),
        (r'^/req/',                                                          "onlyheader"),
    ]
    for pattern, result in patterns:
        if re.match(pattern, path):
            return result
    return "rubbish"

def decide_qr(qr: str):
    try:
        if not in_db(DB_LOGDATA, qr):
            logger.log("QR_not_in_DB")
            raise HTTPException(status_code=422, detail="Unprocessable Content (no such qr code)")
        elif is_expired(DB_LOGDATA, qr):
            logger.log("expired_research")
            raise HTTPException(status_code=406, detail="Not Acceptable (qrcode is expired)")
        elif is_used(DB_LOGDATA, qr):
            logger.log("used_qr")
            raise HTTPException(status_code=410, detail="Gone (qrcode is used)")
        return True

    except Exception as e:
        logger.log("server_error")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error (check database status or whatever...)")

@app.get("/req/{request}")
async def handle_request(request: str, response: Response):
    qr = request[:16]
    request_type = decide_request('/req/' + request)
    print(request_type)

    match request_type:
        case "full":
            if decide_qr(qr):
                push_request(DB_LOGDATA, request)
                response.status_code = status.HTTP_200_OK
                logger.log_message("new_sample")
        case "qr":
            if decide_qr(qr):
                response.status_code = status.HTTP_202_ACCEPTED
                logger.log_message("valid_QR")
        case "part":
            if decide_qr(qr):
                response.status_code = status.HTTP_206_PARTIAL_CONTENT
                logger.log_message("valid_QR_incomplete_request")
        case "onlyheader":
            logger.log_message("only_header")
            response.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        case "rubbish":
            response.status_code = status.HTTP_412_PRECONDITION_FAILED