import mysql.connector
from mysql.connector import Error


def get_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="0368023a",
            database="job_tracker"
        )
        return connection

    except Error as e:
        print("Database connection error:", e)
        raise
