from chatbox import app
from flask import json
from redis import StrictRedis

from .sse_utils import message_to_sse


class RedisMessageServer:
    """Wrap the Redis library with a Python client."""
    def __init__(self):
        self.message_channel = app.config["REDIS_MESSAGE_CHANNEL"]
        self.message_list = app.config["REDIS_MESSAGE_LIST"]
        self.redis_client = StrictRedis(host=app.config["REDIS_HOST"],
                                        port=app.config["REDIS_PORT"],
                                        db=app.config["REDIS_DB"])

    @property
    def event_stream(self):
        """Yield each message from the subscription in SSE format."""
        for message in self.subscribe():
            event = message_to_sse(message["data"])
            yield event

    def add_message(self, msg):
        """
        Add a message to our queue and publish it.
        :param msg: A message object to send: {"author": str, "message": str}
        """
        msg_string = json.dumps(msg)
        self.redis_client.publish(self.message_channel, msg_string)
        self.redis_client.lpush(self.message_list, msg_string)
        self.redis_client.ltrim(self.message_list, 0,
                                app.config["MAX_MESSAGES"]-1)

    def subscribe(self):
        """
        Return a subscription to the message channel.
        """
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.message_channel)
        for item in pubsub.listen():
            if item.get("data") not in (1, None):
                yield item

    def get_messages(self, max_messages):
        """
        Return at most `max_messages` messages.
        :param max_messages:
        :return:
        """
        raw = self.redis_client.lrange(self.message_list, 0, max_messages)
        messages = (m for m in raw if m != b"null")
        messages = (m.decode("utf-8") for m in messages)
        yield from map(json.loads, messages)

    def clear_messages(self):
        """
        Clear the backlog of messages in our Redis list.
        """
        self.redis_client.delete(self.message_list)

