import json
import unittest
import chatbox
from mock import patch

EXAMPLE_MESSAGE_DATA = {
    "text": "This is some test message text!",
    "user": "TestUsername"
}


class TestPostMessage(unittest.TestCase):
    """
    Test functionality associated with posting messages to this API.
    """

    def setUp(self):
        """
        Create a Werkzeug test client to use for sending HTTP requests.
        """
        self.client = chatbox.app.test_client()

    @patch("chatbox.views.message_queue")
    def test_post_message_puts_message_on_queue(self, queue):
        """
        Test that when we post a message to the API, that message is put on
        our queue of messages.
        """
        message_data = EXAMPLE_MESSAGE_DATA
        self.client.post("/messages", data=json.dumps(message_data),
                         content_type="application/json")
        queue.put.assert_called_once_with(message_data)

    def test_post_with_no_content_type(self):
        """
        Test that when we post something without a content type, we get an
        informative JSON error message telling us what the error was.
        """
        response = self.client.post("/messages", data="{}")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(
            dict(error="Content-Type not set in request"),
            response_data
        )
        self.assertEqual(response.status_code, 400)

    def test_post_with_malformed_json(self):
        """
        Test that when we post something with invalid JSON, we get an
        informative JSON error message telling us what the error was.
        It should also include the original request data for reference.
        """
        bad_data = "{"
        response = self.client.post("/messages", data=bad_data,
                                    content_type="application/json")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(
            dict(error="Malformed JSON data in request", original=bad_data),
            response_data
        )
        self.assertEqual(response.status_code, 400)

    def test_post_with_non_utf_8(self):
        """
        Test that when we post something with invalid JSON in some non-UTF-8
        encoding, we get an intelligible error.
        """
        bad_data = bytes([0x81])
        response = self.client.post("/messages", data=bad_data,
                                    content_type="application/json")
        response_data = json.loads(response.data.decode("utf-8"))
        expected_response = \
            dict(error="Malformed JSON data in request",
                 original=(
                       "Original text not available. Server encountered an "
                       "error while trying to decode the content: 'utf-8' "
                       "codec can't decode byte 0x81 in position 0: invalid "
                       "start byte."
                 ))
        self.assertEqual(expected_response, response_data)