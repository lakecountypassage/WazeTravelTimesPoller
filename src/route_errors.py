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

route_errors_json = '../persistence/route_errors.json'


def get_route_errors():
    err_json = helper.read_json(route_errors_json)
    err_route = err_json['routes']
    err_list = []
    for err in err_route:
        err_list.append(err['route_id'])

    return err_list


def route_errors(route_id, route_name, add):
    err_json = helper.read_json(route_errors_json)
    err_dict = dict()

    err_list = get_route_errors()

    if add:
        if route_id not in err_list:
            err_dict['route_id'] = route_id
            err_dict['route_name'] = route_name
            err_json['routes'].append(err_dict)
    else:
        if route_id in err_list:
            for d in err_json['routes']:
                if d['route_id'] == route_id:
                    err_json['routes'].remove(d)


            # err_json['routes'].remove(route_id)

    with open(route_errors_json, 'w') as f:
        json.dump(err_json, f, indent=2)


def route_error_counter():
    err_json = helper.read_json(route_errors_json)

    route_count = len(err_json['routes'])
    if route_count == 0:
        err_json['counter'] = 0
    else:
        err_json['counter'] += 1

    if err_json['counter'] == 15:
        err_json['counter'] = 0
        alert_bad_routes(json.dumps(err_json))

    with open(route_errors_json, 'w') as f:
        json.dump(err_json, f, indent=2)


def alert_bad_routes(text):
    try:
        subject = 'Routes Error'

        if send_oath:
            logging.info('Sending with oauth email')
            send_email_oath.send_message(subject, text, attach=None)
        else:
            logging.info('Sending with regular email')
            send_email.run(subject, text, attach=None)

    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    pass