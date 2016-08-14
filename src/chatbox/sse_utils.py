"""
sse_utils.py

Utilities for dealing with Server-Sent Events (SSEs)
"""


def message_to_sse(message):
    """
    Transform a message into a correctly-formed SSE event.
    :param message: A raw byte-string of message data.
    :return: A correctly-formed SSE event.
    """
    return b"data: " + message + b"\n\n"


def is_valid_sse(event):
    """
    Determine whether an object is a valid SSE byte-string.
    :param event: The object to test.
    :return: Whether the object is a valid SSE.
    """
    if not isinstance(event, bytes):
        return False

    # Assume that the SSE is encoded in UTF-8.
    try:
        event_string = event.decode("utf-8")
    except UnicodeDecodeError:
        return False

    if not event_string.startswith("data: "):
        return False

    if not event_string.endswith("\n\n"):
        return False

    return True
