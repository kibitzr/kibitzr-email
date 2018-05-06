from peewee import DoesNotExist

from .constants import SQLITE_FILE
from .models import database, ProcessedUid, RawEmail


class PersistentUids(object):

    def __init__(self, user_name, check_name, database_name=SQLITE_FILE):
        self.user_name = user_name
        self.check_name = check_name
        database.init(database_name)
        self._table = ProcessedUid
        self._table.connect()

    def only_new(self, uids):
        result = []
        for uids_chunk in self.chunkify(uids, 512):
            result.extend(self._table.only_new(
                self.user_name,
                self.check_name,
                uids_chunk,
            ))
        return result

    def save_uid(self, uid):
        self._table.save_uid(
            self.user_name,
            self.check_name,
            uid,
        )

    @staticmethod
    def chunkify(items, size):
        chunk = []
        for item in items:
            chunk.append(item)
            if len(chunk) >= size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk


class EmailCache(object):

    def __init__(self, user_name, database_name=SQLITE_FILE):
        self.user_name = user_name
        database.init(database_name)
        self._table = RawEmail
        self._table.connect()

    def get(self, uid):
        try:
            return self[uid]
        except KeyError:
            return None

    def __getitem__(self, uid):
        try:
            row = self._table.select().where(
                (self._table.uid == uid) &
                (self._table.user_name == self.user_name)
            ).get()
            return row.raw_email
        except DoesNotExist:
            raise KeyError

    def __setitem__(self, uid, raw_email):
        instance = self._table(
            uid=uid,
            user_name=self.user_name,
            raw_email=raw_email,
        )
        instance.save()
