import logging
import sqlite3


class DatabaseConnection:
    def __init__(self, db_string):
        self.dbconn = None
        self.db_string = db_string

    def __enter__(self):
        self.dbconn = sqlite3.connect(self.db_string)
        logging.debug('Datbase open')
        return self.dbconn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dbconn.close()
        logging.debug('Datbase closed')
