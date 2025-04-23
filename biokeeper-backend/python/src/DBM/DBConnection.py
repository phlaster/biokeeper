import psycopg2

# Implementing context manager protocol (with ... as ...:)
class DBConnection:
    def __init__(self, logdata):
        self.logdata = logdata
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = psycopg2.connect(
            database=self.logdata["db_name"],
            host=self.logdata["db_host"],
            user=self.logdata["db_user"],
            password=self.logdata["db_pass"],
            port=self.logdata["db_port"]
        )
        self.cursor = self.connection.cursor()
        return self.connection, self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
