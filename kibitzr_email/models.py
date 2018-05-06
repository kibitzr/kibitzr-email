from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    BlobField,
)


database = SqliteDatabase(None)


class BaseModel(Model):

    class Meta(object):
        database = database

    connected = False

    @classmethod
    def connect(cls):
        if not cls.connected:
            database.connect()
            # TODO: Find a better way to auto create tables
            database.create_tables([ProcessedUid, RawEmail])
            cls.connected = True


class ProcessedUid(BaseModel):
    check_key = CharField(index=True)
    uid = CharField(index=True)

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


class RawEmail(BaseModel):
    uid = CharField(index=True)
    user_name = CharField(index=True)
    raw_email = BlobField()
