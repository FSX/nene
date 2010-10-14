#!/usr/bin/env python
#-*- coding: utf-8 -*-


import time
import sqlite3


sqlite_db_path = '/home/frank/Projects/Nene/data/logger.db'
connection = None
cursor = None


def connect(api):
    global connection
    global cursor
    connection = sqlite3.connect(sqlite_db_path)
    cursor = connection.cursor()

connect.events = ('pre-connect',)


def log_input(api, matches, origin, dest, text):
    global cursor
    cursor.execute('INSERT INTO messages VALUES (?, ?, ?, ?)', (
        time.mktime(time.gmtime()),
        dest,
        origin['nick'],
        text
    ))
    connection.commit()

log_input.events = ('receive-msg',)


def disconnect(api):
    global connection
    #cursor.close()
    connection.close()

disconnect.events = ('post-disconnect',)
