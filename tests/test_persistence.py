from kibitzr_email.persistence import PersistentUids


def test_processed_uid_filter():
    uids = PersistentUids(
        'user_name',
        'check_name',
        ':memory:',
    )
    uids.save_uid('123')
    filtered = uids.only_new(['123', '456'])
    assert filtered == ['456']
