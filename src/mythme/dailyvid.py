import threading
import time
from typing import Callable, Optional
from mythme.utils import lirc
from mythme.utils.log import logger

DEBOUNCE_INTERVAL = 0.5  # seconds


def start_listener(
    callback: Callable[[str], None],
    socket_path: str = lirc.LIRC_SOCKET,
    debounce_interval: float = DEBOUNCE_INTERVAL,
) -> threading.Thread:
    """Start the LIRC listener in a background daemon thread.

    Invokes callback with the button name for each event. Repeated presses of
    the same button within debounce_interval seconds are ignored.

    :param callback: Function called with the button name for each event
    :type callback: Callable[[str], None]
    :param socket_path: Path to the LIRC socket, defaults to /var/run/lirc/lircd
    :type socket_path: str
    :param debounce_interval: Minimum seconds between processing the same button press
    :type debounce_interval: float
    :return: The background thread running the listener
    :rtype: threading.Thread
    """
    last_button: Optional[str] = None
    last_time: float = 0.0

    def debounced_callback(button: str) -> None:
        nonlocal last_button, last_time
        now = time.monotonic()
        if button == last_button and (now - last_time) < debounce_interval:
            return
        last_button = button
        last_time = now
        callback(button)

    def run() -> None:
        try:
            lirc.listen(debounced_callback, socket_path)
        except Exception as e:
            logger.error(f"LIRC listener error: {e}")

    thread = threading.Thread(target=run, daemon=True, name="lirc-listener")
    thread.start()
    return thread
