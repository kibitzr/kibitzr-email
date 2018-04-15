"""
Integration tests for GNOME Keyring
"""
from keyring import get_keyring

from kibitzr.conf import CompositeCreds


def test_extension_is_discovered():
    creds = CompositeCreds('::')
    assert 'keyring' in creds.extensions


def test_set_and_get_password():
    keyring = get_keyring()
    keyring.set_password('kibitzr_keyring', 'integration test', 'xxx')
    creds = CompositeCreds('::')
    assert creds['keyring']['kibitzr_keyring']['integration test'] == 'xxx'
