import configparser
import json
import logging

import helper
import send_email

config = configparser.ConfigParser(allow_no_value=True)
config.read(helper.get_config_path())

send_oath = config.getboolean("EmailSettings", "SendWithOath")
if send_oath:
    import send_email_oath


def check_persistence_for_buids(buid):
    exists = False
    persistence_json = helper.read_json()
    for uid in persistence_json['buids']:
        if uid['buid'] == buid:
            exists = True

    if not exists:
        persistence_json['buids'].append({
            "buid": buid,
            "counter": 0,
            "last_update": 0
        })

        with open(helper.get_persistence_path(), 'w') as f:
            json.dump(persistence_json, f, indent=2)


def check_update_time(uid, timestamp):
    read_json = helper.read_json()

    for buid in read_json["buids"]:
        if buid["buid"] == uid:
            json_counter = buid["counter"]
            json_last_update = buid["last_update"]
            time_counter = int(json_counter)
            poll_interval = config.getint('Settings', 'FeedError')

            if json_last_update == timestamp:
                # feed has not updated
                if time_counter != 0 and (time_counter % poll_interval) == 0:
                    text = f'It has been {time_counter} polls since the last Waze feed update to {uid}'
                    logging.error(text)

                    try:
                        subject = 'Feed Error'
                        attachment = '../logs/waze_errors.log'

                        if send_oath:
                            logging.info('Sending with oauth email')
                            send_email_oath.send_message(subject, text, attach=attachment)
                        else:
                            logging.info('Sending with regular email')
                            send_email.run(subject, text, attach=attachment)

                    except Exception as e:
                        logging.exception(e)

                buid["counter"] += 1
                with open(helper.get_persistence_path(), 'w') as f:
                    json.dump(read_json, f, indent=2)

                raise Exception("Data already exists in database")
            else:
                # feed has updated
                time_since_update = timestamp - json_last_update
                logging.debug(f"Time since last update {time_since_update}")
                buid["counter"] = 0
                buid["last_update"] = timestamp
                with open(helper.get_persistence_path(), 'w') as f:
                    json.dump(read_json, f, indent=2)


if __name__ == '__main__':
    pass
