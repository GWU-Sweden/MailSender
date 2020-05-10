# -*- coding: utf-8 -*-

from clint.arguments import Args
from clint.textui import prompt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase
from email.header import Header
from email.message import Message
import mimetypes
import os
import pprint
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import tester


def contains_non_ascii_characters(str):
    return not all(ord(c) < 128 for c in str)


def ensure_ascii_only(s):
    if contains_non_ascii_characters(s):
        raise Exception("ERROR: non-ASCII character in plain text")


def smtp_login(host, port, username, password):
    server = smtplib.SMTP(host, port)
    print("> SMTP: EHLO")
    server.ehlo()
    print("> SMTP: STARTTLS")
    server.starttls()
    print("> SMTP: LOGIN")
    server.login(username, password)
    return server


def smtp_logout(server):
    print("> SMTP: QUIT")
    server.quit()


def build_message(sender, sender_address, to, subject, plain_text):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    #ensure_ascii_only(plain_text)

    if contains_non_ascii_characters(plain_text):
        part1 = MIMEText(plain_text, 'plain', 'utf-8')
    else:
        part1 = MIMEText(plain_text, 'plain')
    msg.attach(part1)
    msg.add_header('List-Unsubscribe',
                   '<mailto: {}?subject=Unsubscribe>'.format(sender_address))
    return msg


def send(sender, sender_address, recipients, subject, plain_text):

    if len(recipients) == 0:
        return

    test_msg = build_message(sender, sender_address, None, subject, plain_text)
    test_report_url = tester.test_spammyness(server, sender, test_msg)
    print('\nA test e-mail has been sent to ensure not being flagged as spam.')
    print('To continue please view the report at the following URL and')
    print('PROCEED ONLY if you are happy with it (more than 9.0)')
    print('\n{}\n'.format(test_report_url))
    answer = prompt.query('Continue sending? (y/n)', default="n")
    if not answer.lower() == 'y':
        return

    recipients = list(set(recipients))
    for r in recipients:
        try:
            msg = build_message(sender, sender_address, r, subject, plain_text)
            server.sendmail(sender, r, msg.as_string())
            print("✉️  {}".format(r))
        except Exception, e:
            print(e)
            print("🔥  {}".format(r))


def parse_args():
    args = {}
    for a in Args().all:
        if a.startswith('--'):
            if '=' in a:
                # named param
                i = a.index('=')
                k = a[2:i]
                v = a[i + 1:]
                if not k in args:
                    args[k] = []
                args[k].append(v)
            else:
                # flag
                args[a[2:]] = True
        elif a.startswith('-') and '=' not in a:
            # short flag
            for f in a[1:]:
                args[f] = True
        else:
            # nameless param
            if 'params' not in args:
                args['params'] = []
            args['params'].append(a)
    return args


def load_config(path):
    if not os.path.exists(path):
        raise Exception('Cannot load config: {}'.format(path))
    with open(path, 'rb') as f:
        return yaml.load(f.read(), Loader=Loader)


def load_recipients(path):
    if not os.path.exists(path):
        raise Exception('Cannot load recipients from {}'.format(path))
    with open(path, 'rb') as f:
        return list(set([x.strip() for x in f.readlines()]))


def load_body(path):
    if not os.path.exists(path):
        raise Exception('Cannot load body from {}'.format(path))
    with open(path, 'rb') as f:
        return f.read()


def error_usage(msg):
    raise Exception("Invalid usage: {}".format(msg))


if __name__ == '__main__':
    args = parse_args()

    if not 'config' in args or len(args['config']) > 1:
        error_usage('provide 1 config: --config=yourconfig.yml')
    config = load_config(args['config'][0])

    sender_address = config['sender']
    sender_full = unicode(sender_address)
    if 'sender_name' in config:
        sender_full = "{} <{}>".format(config['sender_name'].encode('utf-8'),
                                       sender_address)

    if not 'to' in args or len(args['to']) > 1:
        error_usage(
            'provide 1 line delimited recipient file: --to=recipients.txt')
    recipients = load_recipients(args['to'][0])

    print("Sending from: {}".format(sender_full))
    print("Sending to\n{}".format(pprint.pformat(recipients)))

    if not 'subject' in args or len(args['subject']) > 1:
        error_usage('provide subject: --subject="Hello There"')
    subject_str = args['subject'][0].decode('utf-8')
    subject = Header(subject_str).encode()
    if not 'plain' in args or len(args['plain']) > 1:
        error_usage('provide plain body file: --plain=body.txt')
    plain = load_body(args['plain'][0])

    print("Authorizing with SMTP server at {}:{}".format(
        config['smtp_host'], config['smtp_port']))
    server = smtp_login(config['smtp_host'], config['smtp_port'],
                        sender_address, config['password'])

    send(sender_full, sender_address, recipients, subject, plain)

    smtp_logout(server)
