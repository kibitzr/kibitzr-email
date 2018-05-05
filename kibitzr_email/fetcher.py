import logging

import six
from kibitzr.conf import settings

from .constants import EMAIL_SSL_HOST, CONF_KEY
from .mailbox import CachingMailbox
from .exceptions import UnexpectedResponse


logger = logging.getLogger(__name__)


class EmailFetcher(object):

    def __init__(self, conf):
        self.conf = conf
        self.mailbox = None  # type: imaplib.IMAP4_SSL
        self.load_conf()

    def fetch_next_email(self):
        mailbox = self.open_inbox()
        try:
            for message in mailbox.fetch_emails(self.name):
                logging.debug('Fetched email; from: %s, subject: %s',
                              message.headers['from'],
                              message.headers['subject'])
                if self.matched(message):
                    return True, message.text
        except UnexpectedResponse:
            pass
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

    def matched(self, mail):
        for header, expected in self.match_rules.items():
            if not mail.headers[header] == expected:
                logger.debug('Filtered out by %s', header)
                return False
        logger.debug('All filters passed')
        return True


def email_fetcher(conf):
    return EmailFetcher(conf).fetch_next_email()
