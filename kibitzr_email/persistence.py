from peewee import SqliteDatabase, Model, CharField


SQLITE_FILE = 'emails.sqlite'
database = SqliteDatabase(None)


class ProcessedUid(Model):
    check_key = CharField(index=True)
    uid = CharField(index=True)

    connected = False

    class Meta:
        database = database

    @classmethod
    def connect(cls):
        if not cls.connected:
            database.connect()
            database.create_tables([cls])
            cls.connected = True

    @classmethod
    def only_new(cls, user_name, check_name, uids):
        rows = cls.select().where(
            (cls.check_key == ':'.join((user_name, check_name))) &
            (cls.uid.in_(uids))
        )
        existing = set([row.uid
                        for row in rows])
        return [uid
                for uid in uids
                if uid not in existing]

    @classmethod
    def save_uid(cls, user_name, check_name, uid):
        cls.create(
            check_key=':'.join((user_name, check_name)),
            uid=uid,
        )

    def __repr__(self):
        return "<ProcessedUid {0} {1}>".format(self.check_key, self.uid)


class PersistentUids(object):

    def __init__(self, user_name, check_name, database_name=SQLITE_FILE):
        self.user_name = user_name
        self.check_name = check_name
        database.init(database_name)
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
