# import mysql.connector
# from mysql.connector import Error
import sqlite3 as sl


def fetch_db():
    db = sl.connect('monitor-downloads.db')

    with db:
        db.execute("""
            CREATE TABLE DOWNLOADS (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                source TEXT 
            );
        """)
    return db


def insert_record(db, data):
    sql = 'INSERT INTO DOWNLOADS (id, name, source) values (?, ?, ?)'
    with db:
        db.execute(sql, data)
