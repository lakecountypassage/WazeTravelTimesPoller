import logging
import os
import sqlite3

import helper


class DatabaseConnection:
    def __init__(self, config):
        self.dbconn = None
        self.config = config

    def __enter__(self):
        use_postgres = self.config.getboolean('Postgres', 'use_postgres')
        if use_postgres:
            db_string = using_postgres(self.config)
            import psycopg2
            self.dbconn = psycopg2.connect(**db_string)
        else:
            db_string = using_sqlite(self.config)
            self.dbconn = sqlite3.connect(db_string)
        logging.debug('Database open')
        return self.dbconn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dbconn.close()
        logging.debug('Database closed')


def using_postgres(config):
    host = str(config.get('Postgres', 'host'))
    database = str(config.get('Postgres', 'database'))
    user = str(config.get('Postgres', 'user'))
    password = str(config.get('Postgres', 'password'))
    database_string = {'host': host, 'database': database, 'user': user, 'password': password}
    return database_string


def using_sqlite(config):
    return os.path.join(helper.get_db_path(), config['Settings']['DatabaseURL'])
