from . import app


class RedisMessageQueue:
    """Provide an interface to treat a Redis server as a Message Queue."""

    def __init__(self):
        self.url = app.config["REDIS_URL"]

    def put(self, item):
        """
        Place `item` on the message queue.
        :param item: The message to be added.
        """

    def last(self, n):
        """
        Returns the last `n` items on the message queue.
        :param n: The number of items to display
        :return: The last `n` items as an iterable.
        """

message_queue = RedisMessageQueue()
