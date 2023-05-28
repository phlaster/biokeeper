from settings.db_settings import db
import psycopg2



conn = psycopg2.connect(database=db["db_name"],
                        host=db["db_host"],
                        user=db["db_user"],
                        password=db["db_pass"],
                        port=db["db_port"]
                        )

cursor = conn.cursor()

data = cursor.execute("SELECT * FROM reseach")

print("This is data:\n", data)
