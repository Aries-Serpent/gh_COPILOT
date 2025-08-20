import logging

from utils.log_utils import log_message


def test_log_message_masks_email(capfd):
    log_message('test_mod', 'contact user@example.com', level=logging.INFO)
    out, err = capfd.readouterr()
    assert 'user@example.com' not in out
    assert '[REDACTED_EMAIL]' in out
    assert 'user@example.com' not in err
