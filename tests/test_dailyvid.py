import time
import threading
from unittest.mock import patch
from mythme.dailyvid import start_listener, DEBOUNCE_INTERVAL


def test_start_listener_returns_thread():
    with patch("mythme.dailyvid.lirc.listen"):
        thread = start_listener(lambda b: None, "/fake/lircd")
    assert isinstance(thread, threading.Thread)
    assert thread.daemon is True
    assert thread.name == "lirc-listener"


def test_start_listener_invokes_callback():
    received: list[str] = []

    def fake_listen(callback, socket_path):
        callback("KEY_OK")

    with patch("mythme.dailyvid.lirc.listen", side_effect=fake_listen):
        thread = start_listener(received.append, "/fake/lircd")
        thread.join(timeout=1)

    assert received == ["KEY_OK"]


def test_debounce_blocks_repeated_press():
    received: list[str] = []

    def fake_listen(callback, socket_path):
        callback("KEY_UP")
        callback("KEY_UP")

    with patch("mythme.dailyvid.lirc.listen", side_effect=fake_listen):
        thread = start_listener(received.append, "/fake/lircd", debounce_interval=10.0)
        thread.join(timeout=1)

    assert received == ["KEY_UP"]


def test_debounce_allows_different_buttons():
    received: list[str] = []

    def fake_listen(callback, socket_path):
        callback("KEY_UP")
        callback("KEY_DOWN")

    with patch("mythme.dailyvid.lirc.listen", side_effect=fake_listen):
        thread = start_listener(received.append, "/fake/lircd", debounce_interval=10.0)
        thread.join(timeout=1)

    assert received == ["KEY_UP", "KEY_DOWN"]


def test_debounce_allows_same_button_after_interval():
    received: list[str] = []

    def fake_listen(callback, socket_path):
        callback("KEY_OK")
        time.sleep(0.05)
        callback("KEY_OK")

    with patch("mythme.dailyvid.lirc.listen", side_effect=fake_listen):
        thread = start_listener(received.append, "/fake/lircd", debounce_interval=0.01)
        thread.join(timeout=1)

    assert received == ["KEY_OK", "KEY_OK"]


def test_listener_logs_error_on_exception():
    with patch("mythme.dailyvid.lirc.listen", side_effect=OSError("no socket")):
        with patch("mythme.dailyvid.logger.error") as mock_log:
            thread = start_listener(lambda b: None, "/fake/lircd")
            thread.join(timeout=1)
    mock_log.assert_called_once()
    assert "LIRC listener error" in mock_log.call_args[0][0]


def test_default_debounce_interval():
    assert DEBOUNCE_INTERVAL == 0.5
