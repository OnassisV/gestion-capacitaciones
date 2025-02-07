import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="108.179.232.52",
        user="hostdifoca",
        password="ubzuR&k-n4Sg",
        database="hostdifo_chapo"
    )