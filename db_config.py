import pymysql.cursors
import os
from dotenv import load_dotenv
from flask import g

load_dotenv()

db_config = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_DATABASE")
}

def get_db_connection():
    return pymysql.connect(
        host = db_config["host"],
        user = db_config["user"],
        password= db_config["password"],
        database= db_config["database"],
        cursorclass = pymysql.cursors.DictCursor
    )

def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
