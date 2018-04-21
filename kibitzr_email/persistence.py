from peewee import SqliteDatabase, Model, CharField


SQLITE_FILE = 'emails.sqlite'
db = SqliteDatabase(SQLITE_FILE)


class ProcessedUid(Model):
    check_key = CharField(index=True)
    uid = CharField(index=True)

    connected = False

    class Meta:
        database = db

    @classmethod
    def connect(cls):
        if not cls.connected:
            db.connect()
            db.create_tables([cls])
            cls.connected = True

    @classmethod
    def only_new(cls, user_name, check_name, uids):
        rows = cls.select(cls.uid).where(
            (cls.check_key == ':'.join((user_name, check_name))) &
            (cls.uid.not_in(uids))
        )
        return [row[0]
                for row in rows]

    @classmethod
    def save_uid(cls, user_name, check_name, uid):
        cls.create(
            check_key=':'.join((user_name, check_name)),
            uid=uid,
        )


class PersistentUids(object):

    def __init__(self, user_name, check_name):
        self.user_name = user_name
        self.check_name = check_name
        self._table = ProcessedUid
        self._table.connect()

    def only_new(self, uids):
        return self._table.only_new(
            self.user_name,
            self.check_name,
            uids,
        )

    def save_uid(self, uid):
        self._table.save_uid(
            self.user_name,
            self.check_name,
            uid,
        )
