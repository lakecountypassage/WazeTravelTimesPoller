import logging
import configparser
import sqlite3
import os

import helper

config = configparser.ConfigParser(allow_no_value=True)
config.read(helper.get_config_path())

USE_POSTGRES = config.getboolean('Postgres', 'use_postgres')
if USE_POSTGRES:
    import psycopg2


class DatabaseConnection:
    def __init__(self):
        self.dbconn = None

    def __enter__(self):
        if USE_POSTGRES:
            db_string = using_postgres()
            self.dbconn = psycopg2.connect(**db_string)
        else:
            db_string = using_sqlite()
            self.dbconn = sqlite3.connect(db_string)
        logging.debug('Datbase open')
        return self.dbconn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dbconn.close()
        logging.debug('Datbase closed')


def using_postgres():
    host = str(config.get('Postgres', 'host'))
    database = str(config.get('Postgres', 'database'))
    user = str(config.get('Postgres', 'user'))
    password = str(config.get('Postgres', 'password'))
    database_string = {'host': host, 'database': database, 'user': user, 'password': password}
    return database_string


def using_sqlite():
    return os.path.join(helper.get_db_path(), config['Settings']['DatabaseURL'])