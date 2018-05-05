import logging
import imaplib
from email import message_from_string
from email.header import decode_header

from .compat import lru_cache
from .persistence import PersistentUids
from .exceptions import UnexpectedResponse


logger = logging.getLogger(__name__)


class CachingMailbox(object):

    @classmethod
    def get(cls, host, user, password):
        instance = cls._get_for_user(host, user)
        instance.login(password)
        return instance

    @staticmethod
    @lru_cache(16)
    def _get_for_user(host, user):
        return CachingMailbox(host, user)

    def __init__(self, host, user):
        logger.debug('Connecting to %s', host)
        self.mailbox = imaplib.IMAP4_SSL(host)
        self.user = user
        self._logged_in = False

    def login(self, password):
        if not self._logged_in:
            logger.debug('Logging in as %s', self.user)
            self.mailbox.login(self.user, password)
            self.mailbox.select("inbox")
            self._logged_in = True

    def fetch_emails(self, check_name):
        uids = self.fetch_uids()
        processed = PersistentUids(self.user, check_name)
        for uid in processed.only_new(uids):
            yield Message(uid, self.fetch_message(uid))
            processed.save_uid(uid)

    def fetch_uids(self):
        result, uids_response = self.mailbox.uid('search', None, "ALL")
        if result != 'OK':
            logger.error('Failed to fetch email UIDs: %s',
                         uids_response)
            raise UnexpectedResponse
        uids = uids_response[0].split()
        logger.debug('Retrieved %d message uids', len(uids))
        return uids

    @lru_cache(512)
    def fetch_message(self, uid):
        result, raw_body = self.mailbox.uid('fetch', uid, '(RFC822)')
        if result != 'OK':
            logger.error('Failed to fetch email body: %s',
                         raw_body)
            raise UnexpectedResponse
        raw_email = raw_body[0][1]
        logger.debug('Fetched message %s body (%s bytes)',
                     uid, len(raw_email))
        return message_from_string(raw_email)


class Message(object):

    def __init__(self, uid, message):
        self.headers = {}
        for header in ['subject', 'to', 'from']:
            text = decode_header(
                message[header].replace('\r\n', ' ')
            )[0][0]
            self.headers[header] = text
        self.uid = uid
        self.body = self.get_body_text(message)

    @property
    def text(self):
        return self.headers['subject'] + '\n' + self.body

    @staticmethod
    def get_body_text(message):
        maintype = message.get_content_maintype()
        if maintype == 'multipart':
            for part in message.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()
        elif maintype == 'text':
            return message.get_payload()
        logging.warning(
            "Could not find text in the email, returning empty string"
        )
        return ''
