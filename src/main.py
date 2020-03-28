#!/usr/bin/env python
import configparser
import json
import logging
import logging.config

import db_conn
import download_data
import helper
import persistence
import send_email

# use config file, not database
config = configparser.ConfigParser(allow_no_value=True)
config.read(helper.config_file)

CONGESTED_PERCENT = config.getint('Settings', 'CongestionPercent')
CONGESTION_EMAIL = False

# add logging
with open(helper.log_config, "r", encoding="utf-8") as f:
    x = json.load(f)

logging.config.dictConfig(x)

logging.debug("<-------- Start -------->")


def write_routes(route_details, db):
    c = db.cursor()
    # insert route data
    try:
        c.execute("""SELECT rid FROM routes WHERE rid = ?""", (route_details[0],))
        r = c.fetchone()

        if r is None:
            logging.debug(route_details)
            c.execute("""INSERT INTO routes VALUES (?,?,?,?,?,?)""", route_details)
    except Exception as e:
        logging.exception(e)
        pass


def write_data(travel_time, db):
    c = db.cursor()
    # insert travel time data
    try:
        logging.info(travel_time)
        c.execute("""INSERT INTO travel_times (rid, c_travel_time, h_travel_time, c_travel_time_min, h_travel_time_min,
                   congested, congested_percent, jam_level, date, time) VALUES (?,?,?,?,?,?,?,?,?,?)""", travel_time)
    except Exception as e:
        logging.exception(e)
        pass


def congestion_table(congested, rid, ddate, ttime, c_travel_time_min, h_travel_time_min, db):
    c = db.cursor()
    c.execute("""SELECT rid FROM routes_congested WHERE rid = ?""", (rid,))
    one = c.fetchone()

    if one is None:
        if congested:
            c.execute("""INSERT INTO routes_congested (rid, ddate, ttime, 
                        c_travel_time_min, h_travel_time_min) VALUES (?,?,?,?,?)""",
                      (rid, ddate, ttime, c_travel_time_min, h_travel_time_min))
    else:
        logging.debug(f'exists in congestion db: {rid}')
        if congested:
            logging.debug(f'continues to be congested: {rid}')
            c.execute("""UPDATE routes_congested SET c_travel_time_min = ?, 
                        h_travel_time_min = ? WHERE rid = ?""", (c_travel_time_min, h_travel_time_min, rid))
        else:
            c.execute("""DELETE FROM routes_congested WHERE rid = ?""", (rid,))


def congestion_counter(db):
    c = db.cursor()
    c.execute("""SELECT rid FROM routes_congested""")
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

    ddate = helper.timestamp_to_date(data['updateTime'])
    ttime = helper.timestamp_to_time(data['updateTime'])

    # parse out only routes
    routes = data['routes']

    # run through the routes for data
    for route in routes:
        counter += 1
        rid = route['id']
        route_name = route['name']
        route_from = route['fromName']
        route_to = route['toName']
        rtype = route['type']
        length = route['length']

        c_travel_time = route['time']
        h_travel_time = route['historicTime']
        jam_level = route['jamLevel']

        c_travel_time_min = helper.time_to_minutes(c_travel_time)
        h_travel_time_min = helper.time_to_minutes(h_travel_time)

        congested = helper.check_congestion(c_travel_time, h_travel_time, CONGESTED_PERCENT)
        congestion_table(congested, rid, ddate, ttime, c_travel_time_min, h_travel_time_min, db)

        route_details = (rid, route_name, route_from, route_to, rtype, length)

        travel_time = (rid, c_travel_time, h_travel_time, c_travel_time_min, h_travel_time_min,
                       congested, CONGESTED_PERCENT, jam_level, ddate, ttime)

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
    ddate = helper.timestamp_to_date(timestamp)
    ttime = helper.timestamp_to_time(timestamp)

    logging.info(f"Waze feed Epoch Time: {timestamp}")
    logging.info(f'Waze feed Date/Time : {ddate} {ttime}')

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

    database_string = config['Settings']['DatabaseURL']
    waze_url_uids = config["WazeUIDS"]
    waze_url_prefix = config['Settings']['WazeURLPrefix']

    with db_conn.DatabaseConnection(database_string) as db:
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
