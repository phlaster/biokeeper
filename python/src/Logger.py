import datetime

class Logger:
    def __init__(self, log_file):
        self.log_file = log_file

    def log(self, msg, return_value = None):
        with open(self.log_file, "a") as f:
            print(datetime.datetime.now(), msg, file=f)
        return return_value

    def clear_logs(self) -> None:
        with open(self.log_file, "w") as f:
            return