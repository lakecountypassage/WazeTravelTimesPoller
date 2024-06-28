import base64
import os
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httplib2
import oauth2client
from apiclient import errors, discovery
from oauth2client import client, tools, file

import helper

SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = os.path.join(helper.get_config_folder_path(), r'client_secret.json')
APPLICATION_NAME = 'Gmail API Python Send Email'
FROM_EMAIL = 'Waze Travel Times <email@email.com>'


def get_email_users(email_users):
    targets = []
    for user in email_users:
        targets.append(user)

    if not targets:
        return None
    else:
        email_addresses = ','.join(str(x) for x in targets)
        return email_addresses


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)

    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def send_message(email_subject, body, email_users, attach=None):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http, cache_discovery=False)
    message = create_message(email_subject, body, email_users, attach)
    send_message_internal(service, "me", message)


def send_message_internal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as err:
        print('An error occurred: %s' % err)


def create_message(email_subject, body, email_users, attach=None):
    message = MIMEMultipart()
    message['to'] = get_email_users(email_users)
    message['from'] = FROM_EMAIL
    message['subject'] = email_subject

    message.attach(MIMEText(body, 'html'))

    if attach is not None:
        fp = open(attach)
        msg = MIMEBase('application', 'octet-stream')
        msg.set_payload(fp.read())
        encoders.encode_base64(msg)
        filename = os.path.basename(attach)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}


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
    string += ('<tr><th>RID</th><th>Road</th><th>To/From</th><th>Current Time</th><th>Historic '
               'Time</th><th>Since</th></tr>')
    string += '</table></body></html>'

    error = 'Travel Times'
    subject = f'Alert: TEST ({time.time()}) '

    # send_message("Test", string, attach='../logs/waze_errors.log')
    send_message("Congestion Summary", string, config['Emails'])
