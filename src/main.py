#!/usr/bin/env python
import configparser
import json
import logging
import logging.config
import os

import db_conn
import download_data
import helper
import persistence
import send_email

# use config file, not database
config = configparser.ConfigParser(allow_no_value=True)
config.read(helper.get_config_path())

CONGESTED_PERCENT = config.getint('Settings', 'CongestionPercent')
CONGESTION_EMAIL = False

# add logging
with open(helper.get_log_config_path(), "r", encoding="utf-8") as f:
    x = json.load(f)
    log_filename = helper.get_logging_filename()[0]
    log_error_filename = helper.get_logging_filename()[1]
    x['handlers']['file']['filename'] = log_filename
    x['handlers']['file_error']['filename'] = log_error_filename

logging.config.dictConfig(x)

logging.debug("<-------- Start -------->")

logging.debug(f'Config path: {helper.get_config_path()}')
logging.debug(f'Log config path: {helper.get_log_config_path()}')
logging.debug(f'Persistence path: {helper.get_persistence_path()}')

# SQL
sql_routes_check = """SELECT route_id FROM routes WHERE route_id = ?"""
sql_routes_insert = """INSERT INTO routes VALUES (?,?,?,?,?,?)"""

sql_write_tt = """INSERT INTO travel_times (route_id, current_tt, historical_tt, current_tt_min, historical_tt_min,
                   congested_bool, congested_percent, jam_level, tt_date_time) VALUES (?,?,?,?,?,?,?,?,?)"""

sql_congested_check = """SELECT route_id FROM routes_congested WHERE route_id = ?"""
sql_congested_insert = """INSERT INTO routes_congested (route_id, congested_date_time, 
                        current_tt_min, historical_tt_min) VALUES (?,?,?,?)"""
sql_congested_update = """UPDATE routes_congested SET current_tt_min = ?, historical_tt_min = ? WHERE route_id = ?"""
sql_congested_remove = """DELETE FROM routes_congested WHERE route_id = ?"""
sql_congested_counter = """SELECT route_id FROM routes_congested"""

USE_POSTGRES = config.getboolean('Postgres', 'use_postgres')
if USE_POSTGRES:
    sql_routes_check = sql_routes_check.replace("?", "%s")
    sql_routes_insert = sql_routes_insert.replace("?", "%s")
    sql_write_tt = sql_write_tt.replace("?", "%s")
    sql_congested_check = sql_congested_check.replace("?", "%s")
    sql_congested_insert = sql_congested_insert.replace("?", "%s")
    sql_congested_update = sql_congested_update.replace("?", "%s")
    sql_congested_remove = sql_congested_remove.replace("?", "%s")
    sql_congested_counter = sql_congested_counter.replace("?", "%s")


def write_routes(route_details, db):
    c = db.cursor()
    # insert route data
    try:
        c.execute(sql_routes_check, (route_details[0],))
        r = c.fetchone()

        if r is None:
            logging.debug(route_details)
            c.execute(sql_routes_insert, route_details)
    except Exception as e:
        logging.exception(e)
        pass


def write_data(travel_time, db):
    c = db.cursor()
    # insert travel time data
    try:
        logging.info(travel_time)
        c.execute(sql_write_tt, travel_time)
    except Exception as e:
        logging.exception(e)
        pass


def congestion_table(congested, route_id, congested_date_time, current_tt_min, historical_tt_min, db):
    c = db.cursor()
    c.execute(sql_congested_check, (route_id,))
    one = c.fetchone()

    if one is None:
        if congested:
            c.execute(sql_congested_insert, (route_id, congested_date_time, current_tt_min, historical_tt_min))
    else:
        logging.debug(f'exists in congestion db: {route_id}')
        if congested:
            logging.debug(f'continues to be congested: {route_id}')
            c.execute(sql_congested_update, (current_tt_min, historical_tt_min, route_id))
        else:
            c.execute(sql_congested_remove, (route_id,))


def congestion_counter(db):
    c = db.cursor()
    c.execute(sql_congested_counter)
    one = c.fetchone()

    if one is None:
        helper.persistence_update('congestion_counter', 0, 'equals')
    else:
        helper.persistence_update('congestion_counter', 1, 'add')

    json = helper.read_json()
    logging.info(f'congestion_counter = {json["congestion_counter"]}')

    congestion_summary_poll = config.getint('Settings', 'CongestionSummaryPoll')
    if json['congestion_counter'] >= congestion_summary_poll:
        global CONGESTION_EMAIL
        CONGESTION_EMAIL = True
        helper.persistence_update('congestion_counter', 0, 'equals')


def process_data(data, db):
    counter = 0

    tt_date_time = helper.timestamp_to_datetime(data['updateTime'])

    # parse out only routes
    routes = data['routes']

    # run through the routes for data
    for route in routes:
        counter += 1
        route_id = route['id']
        route_name = route['name']
        route_from = route['fromName']
        route_to = route['toName']
        route_type = route['type']
        length = route['length']

        current_tt = route['time']
        historical_tt = route['historicTime']
        jam_level = route['jamLevel']

        current_tt_min = helper.time_to_minutes(current_tt)
        historical_tt_min = helper.time_to_minutes(historical_tt)

        congested_bool = helper.check_congestion(current_tt, historical_tt, CONGESTED_PERCENT)
        congestion_table(congested_bool, route_id, tt_date_time, current_tt_min, historical_tt_min, db)

        route_details = (route_id, route_name, route_from, route_to, route_type, length)

        travel_time = (route_id, current_tt, historical_tt, current_tt_min, historical_tt_min,
                       congested_bool, CONGESTED_PERCENT, jam_level, tt_date_time)

        # write data
        try:
            write_routes(route_details, db)
            write_data(travel_time, db)
        except Exception as e:
            logging.exception(e)

    logging.info(f"Route counter: {counter}")


def run(url, uid, db):
    # get data from website
    data = download_data.get_data_from_website(url)
    timestamp = int(data['updateTime'])
    tt_date_time = helper.timestamp_to_datetime(timestamp)

    logging.info(f"Waze feed Epoch Time: {timestamp}")
    logging.info(f'Waze feed Date/Time : {tt_date_time}')

    # check to make sure data is good before proceeding
    try:
        helper.check_for_data_integrity(data)
        logging.debug('data pass integrity check')
    except Exception as e:
        logging.exception(e)
        raise

    # check for existing pull #
    persistence.check_update_time(uid, timestamp)

    # run main
    process_data(data, db)


if __name__ == '__main__':

    logging.info(f'Congested percent: {CONGESTED_PERCENT}')

    waze_url_uids = config["WazeUIDS"]
    waze_url_prefix = config['Settings']['WazeURLPrefix']

    with db_conn.DatabaseConnection() as db:
        for uid in waze_url_uids:
            full_url = f"{waze_url_prefix}{uid}"
            logging.info(f'Waze URL: {full_url}')

            try:
                persistence.check_persistence_for_buids(uid)
                run(full_url, uid, db)
                congestion_counter(db)
            except Exception as e:
                logging.exception(e)
                continue

        # commit all changes
        db.commit()

        # send email
        bool_email = config.getboolean('EmailSettings', 'SendEmailAlerts')
        if send_email.get_email_users() is None:
            bool_email = False

        if bool_email is False:
            logging.info('Not sending emails')
        else:
            if CONGESTION_EMAIL:
                try:
                    send_email.build_email(db)
                except Exception as e:
                    logging.error(e)

    logging.debug("<-------- End -------->")
