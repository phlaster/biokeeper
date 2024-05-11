import datetime

class Logger:
    def __init__(self, log_file):
        self.log_file = log_file

    def log_message(self, msg) -> None:
        with open(self.log_file, "a") as f:
            print(datetime.datetime.now(), msg, file=f)

    def log(self, request, comment) -> None:
        with open(self.log_file, "a") as f:
            ip = request.client_address[0]
            path = request.path[5:]
            print(datetime.datetime.now(), ip, comment, path, file=f, sep=' ')

    def clear_logs(self) -> None:
        with open(self.log_file, "w") as f:
            return