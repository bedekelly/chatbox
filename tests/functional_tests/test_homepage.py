import unittest
import chatbox


class TestHomepage(unittest.TestCase):
    def setUp(self):
        self.app = chatbox.app.test_client()

    def tearDown(self):
        pass

    def test_header_visible(self):
        response = self.app.get("/").data.decode("utf-8")
        self.assertIn("<title>Chatbox</title>", response)
        self.assertIn("<h2>Messages:</h2>", response)
