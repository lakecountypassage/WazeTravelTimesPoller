import json
import logging
import os
import sys
from datetime import datetime

config_file = 'config_lcdot.ini'


def is_frozen():
    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.abspath('..')

    return application_path


def get_config_path():
    return os.path.join(is_frozen(), 'configs\\' + config_file)


def get_log_config_path():
    return os.path.join(is_frozen(), 'configs\\log_config.json')


def get_persistence_path():
    return os.path.join(is_frozen(), 'persistence\\persistence.json')


def get_db_path():
    return os.path.join(is_frozen(), 'database')


def get_logging_filename():
    log_filename = os.path.join(is_frozen(), 'logs\\waze.log')
    log_error_filename = os.path.join(is_frozen(), 'logs\\waze_errors.log')
    return log_filename, log_error_filename


def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp/1000.0).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def time_to_minutes(time_now):
    return round((time_now / 60), 3)


def check_for_data_integrity(data):
    if any([data['updateTime'] == 0, data['updateTime'] == '']):
        raise Exception('Data did not pass the integrity check, cannot proceed')


def check_congestion(time_now, time_historic, congested_percent):
    congestion_threshold = time_historic * (int(congested_percent) / 100)

    if time_now > congestion_threshold:
        congested = True
    else:
        congested = False

    return congested


def read_json(file=None):
    if file is None:
        with open(get_persistence_path(), 'r') as f:
            json_file = json.load(f)
    else:
        with open(file, 'r') as f:
            json_file = json.load(f)

    return json_file


def counter_reset():
    # reset json counter
    logging.debug('Reset json counter')
    persistence_update('counter', 0, 'equals')


def persistence_update(key, value, operator):
    json_file = read_json()

    if operator is 'add':
        json_file[key] += value
    elif operator is 'equals':
        json_file[key] = value

    with open(get_persistence_path(), 'w') as f:
        json.dump(json_file, f, indent=2)

    return json_file


if __name__ == '__main__':
    pass
