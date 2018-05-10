import socket
import logging
import imaplib
import functools

from email import message_from_string
from email.header import decode_header

from .persistence import PersistentUids, EmailCache
from .exceptions import UnexpectedResponse, NetworkOutage


logger = logging.getLogger(__name__)


class CachingMailbox(object):

    _instances = {}

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.login()
        self._fetch_uids = self.relogin_on_error(
            self._fetch_uids_optimistic
        )
        self._fetch_message_from_mailbox = self.relogin_on_error(
            self._fetch_message_from_mailbox_optimistic
        )

    @classmethod
    def get(cls, host, user, password):
        instance = cls._get_for_user(host, user, password)
        return instance

    @classmethod
    def _get_for_user(cls, host, user, password):
        key = (host, user)
        instance = cls._instances.get(key)
        if not instance:
            instance = CachingMailbox(host, user, password)
            cls._instances[key] = instance
        return instance

    def login(self):
        logger.debug('Connecting to %s', self.host)
        try:
            self.mailbox = imaplib.IMAP4_SSL(self.host)
        except socket.gaierror:
            # Network outage, no big deal
            raise NetworkOutage
        logger.debug('Logging in as %s', self.user)
        self.mailbox.login(self.user, self.password)
        self.mailbox.select("inbox")

    def fetch_emails(self, check_name):
        uids = self._fetch_uids()
        processed = PersistentUids(self.user, check_name)
        for uid in processed.only_new(uids):
            processed.save_uid(uid)
            yield self.fetch_message(uid)

    def fetch_all(self):
        uids = self._fetch_uids()
        for uid in uids:
            yield self.fetch_message(uid)

    def relogin_on_error(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except socket.error:
                logging.debug("Socket error occured, reconnecting...")
                self.login()
                return func(*args, **kwargs)
        return wrapped

    def _fetch_uids_optimistic(self):
        result, uids_response = self.mailbox.uid('search', None, "ALL")
        if result != 'OK':
            logger.error('Failed to fetch email UIDs: %s',
                         uids_response)
            raise UnexpectedResponse
        uids = uids_response[0].split()
        logger.debug('Retrieved %d message uids', len(uids))
        return uids

    def fetch_message(self, uid):
        raw_email = self._fetch_message(uid)
        python_message = message_from_string(raw_email)
        return Message(uid, python_message)

    def _fetch_message(self, uid):
        email_cache = EmailCache(self.user)
        raw_email = email_cache.get(uid)
        if raw_email is None:
            raw_email = self._fetch_message_from_mailbox(uid)
            email_cache[uid] = raw_email
        return raw_email

    def _fetch_message_from_mailbox_optimistic(self, uid):
        result, raw_body = self.mailbox.uid('fetch', uid, '(RFC822)')
        if result != 'OK':
            logger.error('Failed to fetch email body: %s',
                         raw_body)
            raise UnexpectedResponse
        raw_email = raw_body[0][1]
        logger.debug('Fetched message %s body (%s bytes)',
                     uid, len(raw_email))
        return raw_email


class Message(object):
    """Convinient email message container"""

    def __init__(self, uid, message):
        self.headers = {}
        for header in ['subject', 'to', 'date', 'from']:
            # Fix utf-8 multiline subjects:
            text = decode_header(
                message[header].replace(u'\r\n', u' ')
            )[0][0]
            self.headers[header] = text
        self.uid = uid
        # Fix line ending:
        self.body = (self.get_body_text(message)
                     .decode('utf-8', 'replace')
                     .replace(u'\r\n', u'\n'))

    @property
    def text(self):
        head = u'\n'.join([
            u'{0}: {1}'.format(key.title(), self.headers[key])
            for key in ('from', 'date', 'subject')
        ])
        return head + u'\n\n' + (u'-'*40) + u'\n\n' + self.body

    @staticmethod
    def get_body_text(message):
        """Return body text as bytes"""
        maintype = message.get_content_maintype()
        if maintype == 'multipart':
            for part in message.get_payload():
                if part.get_content_maintype() == 'text':
                    # Note: decode=True is only for base64, result is still bytes
                    return part.get_payload(decode=True)
        elif maintype == 'text':
            return message.get_payload(decode=True)
        logging.warning(
            "Could not find text in the email, returning empty string"
        )
        return ''
