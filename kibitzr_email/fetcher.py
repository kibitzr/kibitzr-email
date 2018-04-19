import logging
import imaplib
from email import message_from_string
from email.header import decode_header

import six
from kibitzr.conf import settings

from .constants import EMAIL_SSL_HOST, CONF_KEY


logger = logging.getLogger(__name__)


class UnexpectedResponse(RuntimeError):
    pass


class EmailFetcher(object):

    def __init__(self, conf):
        self.conf = conf
        self.mailbox = None

    def fetch_next_email(self):
        self.open_inbox()
        try:
            for mail in self.fetch_emails():
                if self.matched(mail):
                    return True, mail
        except UnexpectedResponse:
            return False, None

    def open_inbox(self):
        self.mailbox = imaplib.IMAP4_SSL(EMAIL_SSL_HOST)
        user, password = self.get_credentials()
        self.mailbox.login(user, password)
        self.mailbox.select("inbox")

    def get_credentials(self):
        """Return (user, password) tuple"""
        credentials = settings().creds.get(CONF_KEY, {})
        user = self.conf.get(CONF_KEY)
        if user:
            return user, credentials[user]
        elif len(credentials) == 1:
            return credentials.items()[0]
        else:
            raise RuntimeError(
                'GMail credentials not defined for check ' + self.conf['name']
            )

    def fetch_emails(self):
        uids = self.fetch_uids()
        for uid in self.filter_processed(uids):
            message = self.fetch_message(uid)
            headers = {}
            for header in ['subject', 'to', 'from']:
                text = decode_header(
                    message[header].replace('\r\n', ' ')
                )[0][0]
                headers[header] = text
            body = StringExtra(get_body_text(message))
            body.headers = headers
            body.uid = uid
            yield body

    def fetch_uids(self):
        result, uids_response = self.mailbox.uid('search', None, "ALL")
        if result != 'OK':
            logger.error('Failed to fetch email UIDs: %s',
                         uids_response)
            raise UnexpectedResponse
        return uids_response[0].split()

    def fetch_message(self, uid):
        result, raw_body = self.mailbox.uid('fetch', uid, '(RFC822)')
        if result != 'OK':
            logger.error('Failed to fetch email body: %s',
                         raw_body)
            raise UnexpectedResponse
        raw_email = raw_body[0][1]
        return message_from_string(raw_email)

    def filter_processed(self, uids):
        return ['33760']
        # return uids

    def matched(self, mail):
        for header, expected in self.conf.get('match', {}).items():
            if not mail.headers[header] == expected:
                return False
        return True


class StringExtra(six.text_type):

    headers = None
    uid = None


def get_body_text(message):
    maintype = message.get_content_maintype()
    if maintype == 'multipart':
        for part in message.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return message.get_payload()


def email_fetcher(conf):
    return EmailFetcher(conf).fetch_next_email()
