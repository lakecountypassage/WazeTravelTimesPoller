import json
import configparser
import logging
import os
import sys
from datetime import datetime

config_file = 'config.ini'


def is_frozen():
    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.abspath('..')

    return application_path


def get_config_path():
    return os.path.join(is_frozen(), 'configs' + os.sep + config_file)


def get_config_folder_path():
    return os.path.join(is_frozen(), 'configs')


def get_log_config_path():
    return os.path.join(is_frozen(), 'configs' + os.sep + 'log_config.json')


def get_route_errors_path():
    return os.path.join(is_frozen(), 'persistence' + os.sep + 'route_errors.json')


def get_db_path():
    return os.path.join(is_frozen(), 'database')


def get_logging_filename():
    log_filename = os.path.join(is_frozen(), 'logs' + os.sep + 'waze.log')
    log_error_filename = os.path.join(is_frozen(), 'logs' + os.sep + 'waze_errors.log')
    return log_filename, log_error_filename


def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp/1000.0).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def time_to_minutes(time_now):
    return round((time_now / 60), 3)


def check_for_data_integrity(data):
    if any([data['updateTime'] == 0, data['updateTime'] == '']):
        raise Exception('Data did not pass the integrity check, cannot proceed')


def get_skip_routes_list():
    skip_list = []
    skip_routes = config['SkipRoutes']
    for x in skip_routes:
        skip_list.append(int(x))

    return skip_list


def get_omit_routes_list():
    omit_list = []
    omit_routes = config['OmitRoutes']
    for x in omit_routes:
        omit_list.append(int(x))

    return omit_list

def get_omit_feed_list():
    omit_list = []
    omit_routes = config['OmitUids']
    for x in omit_routes:
        omit_list.append(x)

    return omit_list


def check_congestion(time_now, time_historic, congested_percent):
    congestion_threshold = time_historic * (int(congested_percent) / 100)

    if time_now > congestion_threshold:
        congested = True
    else:
        congested = False

    return congested


def read_json(file):
    with open(file, 'r') as f:
        json_file = json.load(f)

    return json_file


config = configparser.ConfigParser(allow_no_value=True)
config.read(get_config_path())


def sql_format(sql):
    use_postgres = config.getboolean('Postgres', 'use_postgres')
    if use_postgres:
        sql = sql.replace("?", "%s")
        sql = sql.replace("0", "false")
        sql = sql.replace("1", "true")
    return sql


if __name__ == '__main__':
    pass
