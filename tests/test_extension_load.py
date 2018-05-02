from kibitzr.fetcher.loader import load_extensions
from kibitzr_email import EmailPromoter


def test_kibitzr_email_is_loaded():
    extensions = load_extensions()
    assert extensions
    found = any(
        extension
        for extension in extensions
        if extension is EmailPromoter
    )
    assert found
