import os
import logging

import six
from kibitzr.conf import settings

from .constants import EMAIL_SSL_HOST, CONF_KEY, DOWNLOAD_DIR
from .mailbox import CachingMailbox
from .exceptions import UnexpectedResponse, NetworkOutage


logger = logging.getLogger(__name__)


def email_fetcher(conf):
    return EmailFetcher(conf).fetch_next_email()


def download(user_name):
    logging.getLogger("").setLevel(logging.DEBUG)
    fake_conf = {
        'name': 'download',
        'email': user_name,
    }
    fetcher = EmailFetcher(fake_conf)
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    total = 0
    for message in fetcher.open_inbox().fetch_all():
        path = os.path.join(DOWNLOAD_DIR,
                            '{0}.txt'.format(message.uid))
        logger.debug("Saving %s", path)
        with open(path, 'wt') as fp:
            fp.write(message.text)
        total += 1
    logger.info("Downloaded %d messages to %s",
                total, DOWNLOAD_DIR)


class EmailFetcher(object):

    def __init__(self, conf):
        self.conf = conf
        self.mailbox = None  # type: imaplib.IMAP4_SSL
        self.load_conf()

    def fetch_next_email(self):
        try:
            mailbox = self.open_inbox()
        except NetworkOutage:
            logger.warning("Network is down, skipping fetch")
            return False, None
        try:
            if self.debug_uid:
                message = mailbox.fetch_message(self.debug_uid)
                logger.debug('Fetched email by explicit uid: %s; from: %s, subject: %s',
                             message.uid,
                             message.headers['from'],
                             message.headers['subject'])
                return True, message.text
            for message in mailbox.fetch_emails(self.name):
                logger.debug('Matching email with uid %s; from: %s, subject: %s',
                             message.uid,
                             message.headers['from'],
                             message.headers['subject'])
                if self.matched(message):
                    return True, message.text
        except UnexpectedResponse:
            pass
        logger.debug('No more emails')
        return False, None

    def open_inbox(self):
        return CachingMailbox.get(
            EMAIL_SSL_HOST,
            self.user,
            self.get_password(),
        )

    def load_conf(self):
        credentials = settings().creds.get(CONF_KEY, {})
        user = self.conf.get(CONF_KEY)
        self.name = self.conf['name']
        if isinstance(user, six.string_types):
            # In full form email has email address as value:
            self.user = user
            self.match_rules = self.conf.get('match', {})
            self.get_password = self._get_password_for_explicit_user
        elif len(credentials) == 1:
            # But if credentials define only single email,
            # it can be omitted in conf and
            # have match right in the email
            self.user = credentials.items()[0][0]
            self.match_rules = user
            self.get_password = self._get_default_password
        else:
            raise RuntimeError(
                'EMail credentials not defined for check {0}'
                .format(self.name)
            )

    def _get_password_for_explicit_user(self):
        user = self.conf.get(CONF_KEY)
        credentials = settings().creds.get(CONF_KEY, {})
        return credentials[user]

    @staticmethod
    def _get_default_password():
        credentials = settings().creds.get(CONF_KEY, {})
        return credentials.items()[0][1]

    @property
    def debug_uid(self):
        return self.match_rules.get('uid')

    def matched(self, mail):
        for header, expected in self.match_rules.items():
            if not mail.headers[header] == expected:
                logger.debug('Filtered out by %s', header)
                return False
        logger.debug('All filters passed')
        return True
