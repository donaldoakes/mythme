import socket as socket_module

LIRC_SOCKET = "/var/run/lirc/lircd"


def listen(socket_path: str = LIRC_SOCKET) -> None:
    """Listen for LIRC events and print the button name that was pushed.

    LIRC event format: <code> <repeat> <button> <remote>

    Runs indefinitely until the socket is closed or an exception occurs.

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
                        print(parts[2])
