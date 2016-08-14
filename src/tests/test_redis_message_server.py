from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY

import redis
from chatbox import app
from chatbox.messages import RedisMessageServer
from chatbox.sse_utils import is_valid_sse


EXAMPLE_SUBSCRIBE_ITEMS = [
    {"data": b"""{"author": "bede", "message": "Hello, world!"}"""},
    {"data": b"""{"author": "jack", "message": "Goodbye, world!"}"""}
]

EXAMPLE_MESSAGE = {"author": "bede", "message": "Hello, world!"}
EXAMPLE_MESSAGE2 = {"author": "bede2", "message": "Hola, mundo!"}


class TestRedisMessageServer(TestCase):
    """Test the functionality of the Redis Server wrapper."""

    def setUp(self):
        """
        Ensure that we have a working Redis client connected to the server.
        """
        self.redis_client = redis.StrictRedis()
        app.config["REDIS_DB"] = 1
        try:
            self.redis_client.ping()
        except ConnectionError:
            raise ConnectionError("Redis server not running!")

    @patch.object(RedisMessageServer, "subscribe")
    def test_event_stream(self, subscribe):
        """
        functional-test:
        Test that the event_stream property yields a modified SSE stream.
        This means that each item in the stream should be a correctly-formed
        SSE containing the data from the subscribe() method.
        """
        subscribe_items = subscribe.return_value = EXAMPLE_SUBSCRIBE_ITEMS
        stream = RedisMessageServer().event_stream

        for stream_item, subscribe_item in zip(stream, subscribe_items):
            # Check the item is a correctly-formed SSE.
            self.assertTrue(is_valid_sse(stream_item))
            # Check it contains the subscription data.
            self.assertIn(subscribe_item["data"], stream_item)

    def test_add_message(self):
        """
        unit-test:
        Test that adding a message will do three things: publish it to the
        redis channel, push it to the message list, and truncate that message
        list to MAX_MESSAGES as defined in settings.py.
        """
        # 1. Check we're publishing something to the redis pubsub channel.
        mock_server = MagicMock()
        mock_server.message_channel = "MSG_CHANNEL"
        mock_server.message_list = "MSG_LIST"
        msg_string = '{"author": "bede", "message": "Hello, world!"}'

        # noinspection PyCallByClass,PyTypeChecker
        RedisMessageServer.add_message(mock_server, EXAMPLE_MESSAGE)
        mock_server.redis_client.publish.assert_called_once_with(
            "MSG_CHANNEL", msg_string
        )

        # 2. Check we're pushing the message to the message list.
        mock_server.redis_client.lpush.assert_called_with(
            "MSG_LIST", msg_string
        )

        # 3. Check we're truncating the list to MAX_MESSAGES.
        mock_server.redis_client.ltrim.assert_called_with(
            "MSG_LIST", 0, app.config["MAX_MESSAGES"]-1
        )

    def test_adding_message_end2end(self):
        """
        functional-test:
        Test that adding a message will make it visible on the Redis server.
        """
        message_server = RedisMessageServer()
        message_server.add_message(EXAMPLE_MESSAGE2)
        msg, *_ = list(message_server.get_messages(1))
        self.assertEqual(msg, EXAMPLE_MESSAGE2)

    def test_messages_are_truncated(self):
        """
        functional-test:
        Test that adding more messages than MAX_MESSAGES means that some
        will be truncated from the end, so that at most MAX_MESSAGES are
        stored in the Redis database.
        """
        app.config["MAX_MESSAGES"] = 3
        message_server = RedisMessageServer()
        message_server.add_message(EXAMPLE_MESSAGE2)
        for msg in range(3):
            message_server.add_message(EXAMPLE_MESSAGE)
        msgs = list(message_server.get_messages(5))
        self.assertEqual(len(msgs), 3)

    def test_clear_messages(self):
        """
        functional-test:
        Test that clearing messages does what it says on the tin.
        """
        message_server = RedisMessageServer()
        message_server.clear_messages()
        message_server.add_message(EXAMPLE_MESSAGE)
        message_server.add_message(EXAMPLE_MESSAGE2)
        self.assertEqual(len(list(message_server.get_messages(100))), 2)
        message_server.clear_messages()
        self.assertEqual(len(list(message_server.get_messages(100))), 0)

    def tearDown(self):
        """
        On teardown, make sure our test database is clear.
        """
        RedisMessageServer().clear_messages()
