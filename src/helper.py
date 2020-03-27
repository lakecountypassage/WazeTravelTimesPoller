import json
import logging
import time

config_file = r'../configs/config.ini'
log_config = r'../configs/log_config.json'
persistence_file = r'../persistence/persistence.json'


def timestamp_to_date(timestamp):
    return time.strftime("%m/%d/%Y", time.localtime(timestamp / 1000))


def timestamp_to_time(timestamp):
    return time.strftime("%H:%M:%S", time.localtime(timestamp / 1000))


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
        with open(persistence_file, 'r') as f:
            tmp = json.load(f)
    else:
        with open(file, 'r') as f:
            tmp = json.load(f)

    return tmp


def counter_reset():
    # reset json counter
    logging.debug('Reset json counter')
    persistence_update('counter', 0, 'equals')


def persistence_update(key, value, operator):
    tmp = read_json()

    if operator is 'add':
        tmp[key] += value
    elif operator is 'equals':
        tmp[key] = value

    with open(persistence_file, 'w') as f:
        json.dump(tmp, f, indent=2)

    return tmp


if __name__ == '__main__':
    pass
