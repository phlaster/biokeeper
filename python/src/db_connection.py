import psycopg2

def connect2db(logdata):
    connection = psycopg2.connect(
        database = logdata["db_name"],
        host =     logdata["db_host"],
        user =     logdata["db_user"],
        password = logdata["db_pass"],
        port =     logdata["db_port"])
    cursor = connection.cursor()
    return connection, cursor