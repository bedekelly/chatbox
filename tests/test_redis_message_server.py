from unittest import TestCase
from unittest.mock import patch, MagicMock

import redis
from messages import RedisMessageServer
from sse_utils import is_valid_sse

EXAMPLE_SUBSCRIBE_ITEMS = [
    {"data": b"""{"author": "bede", "message": "Hello, world!"}"""},
    {"data": b"""{"author": "jack", "message": "Goodbye, world!"}"""}
]


class TestRedisMessageServer(TestCase):
    """Test the functionality of the Redis Server wrapper."""

    def setUp(self):
        """
        Ensure that we have a working Redis client connected to the server.
        """
        self.redis_client = redis.StrictRedis()
        try:
            self.redis_client.ping()
        except ConnectionError:
            self.fail("Redis server not running!")

    @patch.object(RedisMessageServer, "subscribe")
    def test_event_stream(self, subscribe):
        """
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

    @patch.object(RedisMessageServer, "redis_client")
    def test_add_message(self, mock_redis_client):
        mock_redis_client.publish.assert_called_once_with(

            """{"data": b'{"author": "bede", "message": "Hello, world!"}'}"""
        )

    def test_subscribe(self):
        self.fail()

    def test_get_messages(self):
        self.fail()

    def test_clear_messages(self):
        self.fail()
