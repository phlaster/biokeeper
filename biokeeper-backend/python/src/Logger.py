import datetime

class AlwaysFalseString(str):
    def __new__(cls, value):
        return super(AlwaysFalseString, cls).__new__(cls, value)
    
    def __bool__(self):
        return False


class Logger:
    def __init__(self, log_file):
        self.log_file = log_file

    def log(self, msg, return_value=None):
        with open(self.log_file, "a") as f:
            print(datetime.datetime.now(), msg, file=f)
        return AlwaysFalseString(msg)

    def clear_logs(self) -> None:
        with open(self.log_file, "w") as f:
            return
