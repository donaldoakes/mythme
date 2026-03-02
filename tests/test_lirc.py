from unittest.mock import MagicMock, patch
from mythme.utils.lirc import listen, LIRC_SOCKET


def make_socket_mock(messages: list[bytes]) -> MagicMock:
    """Return a mock socket that yields the given byte sequences then empty bytes."""
    mock_sock = MagicMock()
    mock_sock.__enter__ = MagicMock(return_value=mock_sock)
    mock_sock.__exit__ = MagicMock(return_value=False)
    mock_sock.recv.side_effect = messages + [b""]
    return mock_sock


def test_listen_invokes_callback_with_button_name():
    event = b"0000000000000001 00 KEY_UP Remote\n"
    mock_sock = make_socket_mock([event])
    received: list[str] = []
    with patch("mythme.utils.lirc.socket_module.socket", return_value=mock_sock):
        listen(received.append, "/fake/lircd")
    assert received == ["KEY_UP"]


def test_listen_multiple_events():
    events = b"0000000000000001 00 KEY_UP Remote\n0000000000000002 00 KEY_DOWN Remote\n"
    mock_sock = make_socket_mock([events])
    received: list[str] = []
    with patch("mythme.utils.lirc.socket_module.socket", return_value=mock_sock):
        listen(received.append, "/fake/lircd")
    assert received == ["KEY_UP", "KEY_DOWN"]


def test_listen_ignores_malformed_lines():
    events = b"bad\n0000000000000001 00 KEY_OK Remote\n"
    mock_sock = make_socket_mock([events])
    received: list[str] = []
    with patch("mythme.utils.lirc.socket_module.socket", return_value=mock_sock):
        listen(received.append, "/fake/lircd")
    assert received == ["KEY_OK"]


def test_listen_handles_split_messages():
    part1 = b"0000000000000001 00 KEY_"
    part2 = b"SELECT Remote\n"
    mock_sock = make_socket_mock([part1, part2])
    received: list[str] = []
    with patch("mythme.utils.lirc.socket_module.socket", return_value=mock_sock):
        listen(received.append, "/fake/lircd")
    assert received == ["KEY_SELECT"]


def test_default_socket_path():
    assert LIRC_SOCKET == "/var/run/lirc/lircd"


def test_listen_connects_to_socket_path():
    mock_sock = make_socket_mock([b""])
    with patch("mythme.utils.lirc.socket_module.socket", return_value=mock_sock):
        listen(lambda b: None, "/custom/lircd")
    mock_sock.connect.assert_called_once_with("/custom/lircd")
