import logging

from kibitzr.fetcher.base import BasePromoter

from .constants import CONF_KEY, PROMOTER_PRIORITY


logger = logging.getLogger(__name__)


class EmailPromoter(BasePromoter):

    PRIORITY = PROMOTER_PRIORITY

    def __init__(self, conf):
        from .fetcher import email_fetcher
        super(EmailPromoter, self).__init__(conf)
        self.fetcher_func = email_fetcher

    @staticmethod
    def is_applicable(conf):
        """Return whether this promoter is applicable for given conf"""
        return bool(conf.get(CONF_KEY))

    def log_announcement(self):
        logger.info(u"Fetching next email for %s",
                    self.conf['name'])
