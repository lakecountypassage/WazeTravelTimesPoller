#!/usr/bin/env python
import configparser
import json
import logging
import logging.config
from datetime import datetime, timedelta

from dateutil.parser import parse

import db_conn
import deleted_routes
import download_data
import helper
import route_errors
import send_email

# use config file, not database
config = configparser.ConfigParser(allow_no_value=True)
config.read(helper.get_config_path())

ARCHIVE_DATA = config.getboolean('Settings', 'ArchiveData', fallback=True)
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

# SQL
sql_routes_check = """SELECT route_id, feed_id, feed_name, deleted FROM routes WHERE route_id = ?"""
sql_routes_insert = """INSERT INTO routes VALUES (?,?,?,?,?,?,?,?,?)"""
sql_route_update = """UPDATE routes SET feed_id = ?, feed_name = ? WHERE route_id = ?"""
sql_delete_update = """UPDATE routes SET deleted = ? WHERE route_id = ?"""

sql_write_tt = """INSERT INTO travel_times (route_id, current_tt, historical_tt, current_tt_min, historical_tt_min,
                   congested_bool, congested_percent, jam_level, tt_date_time) VALUES (?,?,?,?,?,?,?,?,?)"""

sql_congested_check = """SELECT route_id FROM routes_congested WHERE route_id = ?"""
sql_congested_insert = """INSERT INTO routes_congested (route_id, congested_date_time, 
                        current_tt_min, historical_tt_min) VALUES (?,?,?,?)"""
sql_congested_update = """UPDATE routes_congested SET current_tt_min = ?, historical_tt_min = ? WHERE route_id = ?"""
sql_congested_remove = """DELETE FROM routes_congested WHERE route_id = ?"""
sql_congested_counter = """SELECT route_id FROM routes_congested"""
sql_delete_bad_congestion = """DELETE FROM routes_congested WHERE congested_date_time < ?"""


def write_routes(route_details, db):
    c = db.cursor()
    # insert route data
    try:
        c.execute(helper.sql_format(sql_routes_check), (route_details[0],))
        r = c.fetchone()

        if r is None:
            logging.debug(route_details)
            c.execute(helper.sql_format(sql_routes_insert), route_details)

        else:
            # update deleted column
            if r[3] or r[3] is None:
                c.execute(helper.sql_format(sql_delete_update), (route_details[8], route_details[0]))

            # add feed id and name if they don't exist
            if r[1] is None or r[2] is None:
                logging.debug('updating route to include feed id and name')
                route_update = (route_details[6], route_details[7], route_details[0])
                c.execute(helper.sql_format(sql_route_update), route_update)

    except Exception as e:
        logging.exception(e)
        pass


def write_data(travel_time, db):
    c = db.cursor()
    # insert travel time data
    try:
        logging.info(travel_time)
        c.execute(helper.sql_format(sql_write_tt), travel_time)
    except Exception as e:
        logging.exception(e)
        pass


def congestion_table(congested, route_id, congested_date_time, current_tt_min, historical_tt_min, omit, db):
    c = db.cursor()
    c.execute(helper.sql_format(sql_congested_check), (route_id,))
    one = c.fetchone()

    # remove routes in table if omit
    if omit:
        logging.debug(f"Omitting routes from congestion alerting: {route_id}")
        if one is not None:
            logging.debug(f"Removing omitted from congestion table: {route_id}")
            c.execute(helper.sql_format(sql_congested_remove), (route_id,))
    else:
        if one is None:
            if congested:
                c.execute(helper.sql_format(sql_congested_insert),
                          (route_id, congested_date_time, current_tt_min, historical_tt_min))
        else:
            logging.debug(f'exists in congestion db: {route_id}')
            if congested:
                logging.debug(f'continues to be congested: {route_id}')
                c.execute(helper.sql_format(sql_congested_update), (current_tt_min, historical_tt_min, route_id))
            else:
                c.execute(helper.sql_format(sql_congested_remove), (route_id,))


def delete_bad_congestion():
    delete_bad_congestion_time_delay = config.getint("Settings", "DeleteStaleCongstedRoutesInMin", fallback=120)
    logging.debug(f"DeleteStaleCongstedRoutesInMin = {delete_bad_congestion_time_delay}")
    if delete_bad_congestion_time_delay == 0:
        logging.info("Not attempting to delete bad congestion routes.")
        return

    time_delay = datetime.now() - timedelta(minutes=delete_bad_congestion_time_delay)
    logging.info(f"Deleting any bad congestion older than: {time_delay}")
    try:
        c = db.cursor()
        sql = helper.sql_format(sql_delete_bad_congestion)
        c.execute(sql, (time_delay,))
    except Exception as ex:
        logging.exception(ex)


def send_congestion_email():
    # send email
    if config.getboolean('EmailSettings', 'SendEmailAlerts', fallback=False) is False:
        logging.info('Emails are turned off in the cofiguration file.')
        return

    if send_email.get_email_users() is None:
        logging.info('Emails are not sending, you have no user recipients.')
        return

    config_email_delay = config.getint("Settings", "CongestionEmailDelayInMin", fallback=10)
    last_congestion_email = parse(helper.read_json()['last_congestion_email'])

    # if last sent email is older than now - 10min
    if last_congestion_email > datetime.now() - timedelta(minutes=config_email_delay):

        logging.debug(
            f"Last congestion email was sent at: {last_congestion_email}. "
            f"Won't send another for email for "
            f"{config_email_delay - int((datetime.now() - last_congestion_email).total_seconds() / 60)} minute/s.")

    # last email was sent more than X min ago -- send another, if there are routes to send
    else:
        # get the congested routes
        c = db.cursor()
        sql = helper.sql_format('''SELECT routes_congested.route_id, current_tt_min, historical_tt_min,
                        route_name, route_from, route_to, congested_date_time
                        FROM routes_congested
                        INNER JOIN routes ON routes_congested.route_id=routes.route_id''')

        c.execute(sql)
        congested_routes = c.fetchall()

        if len(congested_routes) == 0:
            logging.info("There are currently no congested routes. Not sending an email.")
            return

        logging.info(f"Congestion email was sent more than {config_email_delay} min ago, sending another one.")

        try:
            send_email.build_email(congested_routes)
        except Exception as e:
            logging.error(e)


def process_data(uid, data, db):
    counter = 0

    tt_date_time = helper.timestamp_to_datetime(data['updateTime'])

    # parse out only routes
    routes = data['routes']

    # get the feed name
    feed_name = data['name']

    # get current route errors
    err_list = route_errors.get_route_errors()

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

        route_list.append(route_id)

        if route_id in skip_routes:
            logging.warning(f'Route {route_id} is set to skip, will not process or log.')
            continue

        if current_tt == -1:
            logging.warning(f'Route {route_id} is showing -1, skipping for now')
            route_errors.set_route_errors(route_id, route_name, add=True)
            continue  # move to next route, do not archive
        elif route_id in err_list:
            route_errors.set_route_errors(route_id, route_name, add=False)

        omit = False
        if route_id in omit_routes or uid in omit_feeds:
            omit = True

        current_tt_min = helper.time_to_minutes(current_tt)
        historical_tt_min = helper.time_to_minutes(historical_tt)

        congested_bool = helper.check_congestion(current_tt, historical_tt, CONGESTED_PERCENT)
        congestion_table(congested_bool, route_id, tt_date_time, int(current_tt_min), int(historical_tt_min), omit, db)

        route_details = (route_id, route_name, route_from, route_to, route_type, length, uid, feed_name, False)

        travel_time = (
            route_id, current_tt, historical_tt, current_tt_min, historical_tt_min, congested_bool, CONGESTED_PERCENT,
            jam_level, tt_date_time)

        # write data
        try:
            write_routes(route_details, db)
            if ARCHIVE_DATA:
                write_data(travel_time, db)
        except Exception as e:
            logging.exception(e)

    logging.info(f"Route counter: {counter}")


def feed_check_good(timestamp):
    is_feed_good = True

    feed_delay_error_time = config.getint("Settings", "FeedErrorInMin", fallback=30)
    if feed_delay_error_time != 0:  # skip error checking if feed_delay_error_time is 0
        time_delay = datetime.now() - timedelta(minutes=feed_delay_error_time)
        logging.debug(f"Checking if the feed is older than: {time_delay}")

        if datetime.fromtimestamp(timestamp / 1000.0) < time_delay:
            is_feed_good = False

            text = f'It has been over {feed_delay_error_time} min since the last Waze feed update to {uid}.'
            logging.error(text)

            send_oath = config.getboolean("EmailSettings", "SendWithOath")
            try:
                subject = 'Feed Error'

                if send_oath:
                    logging.info('Sending with oauth email')
                    import send_email_oath
                    send_email_oath.send_message(subject, text)
                else:
                    logging.info('Sending with regular email')
                    send_email.run(subject, text)

            except Exception as e:
                logging.exception(e)

    return is_feed_good


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
    except Exception as e:
        logging.exception(e)
        raise

    if feed_check_good(timestamp):
        process_data(uid, data, db)
    else:
        logging.error("Something is wrong with the feed, skipping processing.")


if __name__ == '__main__':

    logging.info(f'Congested percent: {CONGESTED_PERCENT}')

    waze_url_uids = config["WazeUIDS"]
    waze_url_prefix = config['Settings']['WazeURLPrefix']

    skip_routes = helper.get_skip_routes_list()
    logging.info(f'Skip these routes completely: {skip_routes}')
    route_errors.remove_deleted_routes(skip_routes)

    omit_routes = helper.get_omit_routes_list()
    logging.info(f'Omit these routes from congestion alerting: {omit_routes}')

    omit_feeds = helper.get_omit_feed_list()
    logging.info(f'Omit these feeds from congestion alerting: {omit_feeds}')

    route_list = []

    with db_conn.DatabaseConnection() as db:
        for uid in waze_url_uids:
            full_url = f"{waze_url_prefix}{uid}"
            logging.info(f'Waze URL: {full_url}')

            try:
                run(full_url, uid, db)
            except Exception as e:
                logging.exception(e)
                continue

        # run route error counter check after processing the data
        route_errors.route_error_counter()

        check_deleted = config.getboolean('Settings', 'CheckForDeleted')
        logging.debug(f'Check for deleted routes: {check_deleted}')
        if check_deleted:
            try:
                # check for deleted routes
                # deleted_routes.set_route_list(route_list)
                del_routes = deleted_routes.DeletedRoutes(db, route_list)
                del_routes.run()

                # remove deleted routes from persistence
                route_errors.remove_deleted_routes(del_routes.get_deleted_routes())
            except Exception as e:
                logging.exception(e)

        # delete bad congestion
        delete_bad_congestion()

        # send email
        send_congestion_email()

        # commit all changes
        db.commit()

    logging.debug("<-------- End -------->")
