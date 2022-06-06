import configparser
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

config = configparser.ConfigParser(allow_no_value=True)
config.read(helper.get_config_path())

send_oath = config.getboolean("EmailSettings", "SendWithOath")
if send_oath:
    import send_email_oath


def get_email_users():
    targets = []
    for user in config["Emails"]:
        targets.append(user)

    if not targets:
        return None
    else:
        # email_addresses = ','.join(str(x) for x in targets)
        return targets


def build_email(db):
    string = '<html><head><style>table, th, td {border: 1px solid black;}</style></head><body>'
    string += '<table width="100%">'
    string += '<tr><th>RID</th><th>Road</th><th>To/From</th><th>Current Time</th><th>Historic Time</th><th>Since</th></tr>'

    c = db.cursor()
    c.execute('''SELECT routes_congested.route_id, current_tt_min, historical_tt_min, 
                    route_name, route_from, route_to, congested_date_time
                    FROM routes_congested
                    INNER JOIN routes ON routes_congested.route_id=routes.route_id''')
    all = c.fetchall()

    for each in all:
        rid = each[0]
        c_min = each[1]
        h_min = each[2]
        route_name = each[3]
        route_from = each[4]
        route_to = each[5]
        ddate = each[6]

        string += '<tr>'
        string += f'<td>{rid}</td>'
        string += f'<td>{route_name}</td>'
        string += f'<td>{route_from} to {route_to}</td>'
        string += f'<td>{c_min}</td>'
        string += f'<td>{h_min}</td>'
        string += f'<td>{ddate}</td>'
        string += '</tr>'

    string += "</table>"
    string += '</body></html>'

    try:
        subject = 'Congestion Summary'

        if send_oath:
            logging.info('Sending with oauth email')
            send_email_oath.send_message(subject, string)
        else:
            logging.info('Sending with regular email')
            run('Congestion Summary', string, attach=None, type='html')

    except Exception as e:
        logging.exception(e)


def run(subject, body, attach=None, type=None):
    EMAIL_USER = config["EmailSettings"]["Username"]
    EMAIL_PWD = config["EmailSettings"]["Password"]

    if EMAIL_USER == '' or EMAIL_PWD == '':
        raise Exception("You are missing email username or password")

    logging.info('Attempting to send email')

    # smtp_ssl_host = 'smtp.gmail.com'
    smtp_ssl_host = config.get('EmailSettings', 'SMTP_SSL_Host')
    smtp_ssl_port = config.getint('EmailSettings', 'SMTP_SSL_Port')
    nickname = config.get('EmailSettings', 'From_Nickname')
    sender = formataddr((nickname, config.get('EmailSettings', 'SMTP_Sender')))
    # targets = get_email_users()

    msg = MIMEMultipart()

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(get_email_users())

    if type == 'html':
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
    server.login(EMAIL_USER, EMAIL_PWD)
    server.sendmail(sender, get_email_users(), msg.as_string())
    server.quit()
    logging.info('Email sent')


if __name__ == '__main__':
    # test email by running this file
    string = '<html><head><style>table, th, td {border: 1px solid black;}</style></head><body>'
    string += '<table width="50%">'
    string += '<tr><th>RID</th><th>Road</th><th>To/From</th><th>Current Time</th><th>Historic Time</th><th>Since</th></tr>'
    string += '</table></body></html>'

    error = 'Travel Times'
    subject = f'Alert: TEST ({time.time()}) '
    run(subject, string, attach=None, type='html')
