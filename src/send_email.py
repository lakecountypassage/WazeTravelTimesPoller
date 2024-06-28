import logging
import os
import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import helper


def get_email_users(email_users):
    targets = []
    for user in email_users:
        targets.append(user)

    if not targets:
        return None
    else:
        # email_addresses = ','.join(str(x) for x in targets)
        return targets


def build_email(routes, config_file):
    s = ("""<html lang="en">
                    <head>    
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            table, th, td {
                              border: 1px solid #ddd;
                              border-collapse: collapse;
                            }
                            table {
                                background-color: white;
                                overflow: hidden;
                                font-size:85%;
                            }
                            th, td {
                                padding: 5px;
                                text-align: left;
                            }
                            th {
                                background-color: #4a6b8a;  /* Lighter blue-grey color */
                                color: white;
                            }
                        </style>
                    </head>
                <body>""")
    s += '<table>'
    s += '<tr><th>RID</th><th>Road</th><th>To/From</th><th>Current Time</th><th>Historic Time</th><th>Since</th></tr>'

    i = 1
    for each in routes:
        i += 1
        rid = each[0]
        c_min = each[1]
        h_min = each[2]
        route_name = each[3]
        route_from = each[4]
        route_to = each[5]
        ddate = each[6]

        if i % 2 == 0:
            s += '<tr>'
        else:
            s += '<tr style="background-color:#e6f3ff">'
        s += f'<td>{rid}</td>'
        s += f'<td>{route_name}</td>'
        s += f'<td>{route_from} to {route_to}</td>'
        s += f'<td>{c_min}</td>'
        s += f'<td>{h_min}</td>'
        s += f'<td>{ddate}</td>'
        s += '</tr>'

    s += "</table>"
    s += '</body></html>'

    # logging.debug(string)

    try:
        email_subject = 'Congestion Summary'

        send_oath = config_file.getboolean("EmailSettings", "SendWithOath")
        if send_oath:
            logging.info('Sending with oauth email')
            import send_email_oath
            email_users = config['Emails']
            send_email_oath.send_message(email_subject, s, email_users)
        else:
            logging.info('Sending with regular email')
            run(email_subject, s, config_file, attach=None, email_type='html')

    except Exception as e:
        logging.exception(e)


def run(email_subject, body, config_file, attach=None, email_type=None):
    email_username = config_file["EmailSettings"]["Username"]
    email_pwd = config_file["EmailSettings"]["Password"]
    email_users = config_file["Emails"]

    if email_username == '' or email_pwd == '':
        raise Exception("You are missing email username or password")

    logging.info('Attempting to send email')

    # smtp_ssl_host = 'smtp.gmail.com'
    smtp_ssl_host = config_file.get('EmailSettings', 'SMTP_SSL_Host')
    smtp_ssl_port = config_file.getint('EmailSettings', 'SMTP_SSL_Port')
    nickname = config_file.get('EmailSettings', 'From_Nickname')
    sender = formataddr((nickname, config_file.get('EmailSettings', 'SMTP_Sender')))
    # targets = get_email_users()

    msg = MIMEMultipart()

    msg['Subject'] = email_subject
    msg['From'] = sender
    msg['To'] = ', '.join(get_email_users(email_users))

    if email_type == 'html':
        msg.attach(MIMEText(body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

    if attach is not None:
        attachment = open(attach, "rb")

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attach))

        msg.attach(part)

    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(email_username, email_pwd)
    server.sendmail(sender, get_email_users(email_users), msg.as_string())
    server.quit()
    logging.info('Email sent')

    # update the persistence file with the new datetime when the email was sent
    import json
    from datetime import datetime
    json_file = helper.read_json()
    with open(helper.get_persistence_path(), 'w') as f:
        json_file['last_congestion_email'] = datetime.now().strftime(helper.time_format)
        json.dump(json_file, f, indent=2)


if __name__ == '__main__':
    import configparser
    import options

    # get command line arguments, if any
    args = options.__args_parser('Waze Travel Times Poller')

    # use config file, not database
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(helper.get_config_path(args.config_path))

    # test email by running this file
    string = '<html><head><style>table, th, td {border: 1px solid black;}</style></head><body>'
    string += '<table width="50%">'
    string += '<tr><th>RID</th><th>Road</th><th>To/From</th><th>Current Time</th><th>Historic Time</th><th>Since</th></tr>'
    string += '</table></body></html>'

    error = 'Travel Times'
    subject = f'Alert: TEST ({time.time()}) '
    run(subject, string, config, attach=None, email_type='html')
