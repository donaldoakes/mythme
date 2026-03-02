import socket as socket_module
from typing import Callable

LIRC_SOCKET = "/var/run/lirc/lircd"


def listen(callback: Callable[[str], None], socket_path: str = LIRC_SOCKET) -> None:
    """Listen for LIRC events and invoke callback with the button name that was pushed.

    LIRC event format: <code> <repeat> <button> <remote>

    Runs indefinitely until the socket is closed or an exception occurs.

    :param callback: Function called with the button name for each event
    :type callback: Callable[[str], None]
    :param socket_path: Path to the LIRC socket, defaults to /var/run/lirc/lircd
    :type socket_path: str
    """
    with socket_module.socket(socket_module.AF_UNIX, socket_module.SOCK_STREAM) as sock:
        sock.connect(socket_path)
        buf = ""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            buf += data.decode("utf-8")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 3:
                        callback(parts[2])
