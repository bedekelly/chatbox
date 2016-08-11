import unittest
import chatbox


class TestHomepage(unittest.TestCase):
    """
    Test the basic visibility of the homepage.
    """

    def setUp(self):
        """
        Create a Werkzeug test client to use for HTTP requests.
        """
        self.app = chatbox.app.test_client()

    def test_titles_visible(self):
        """
        Check that the title and header elements are visible and contain
        the correct text, on the root location.
        """
        response = self.app.get("/").data.decode("utf-8")
        self.assertIn("<title>Chatbox</title>", response)
        self.assertIn("<h2>Messages:</h2>", response)
