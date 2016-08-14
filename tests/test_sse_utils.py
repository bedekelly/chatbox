from unittest import TestCase

from sse_utils import is_valid_sse


class TestIsValidSSE(TestCase):
    def test_not_bytes(self):
        """Check that any non-bytes data is considered invalid."""
        self.assertFalse(is_valid_sse("data: test\n\n"))

    def test_non_utf8(self):
        """Check that any bytestring encoded outside of utf-8 is invalid."""
        self.assertFalse(is_valid_sse(bytes([0x81])))

    def test_startswith_data(self):
        """Check that anything that doesn't start with data is invalid."""
        invalid_bytes = bytes("stuff: data\n\n", encoding="utf-8")
        self.assertFalse(is_valid_sse(invalid_bytes))

    def test_endswith_newlines(self):
        """Check that anything not ending with two newlines is invalid."""
        invalid_bytes = bytes("data: something\n\n  blah \n", encoding="utf-8")
        self.assertFalse(is_valid_sse(invalid_bytes))

    def test_valid_sse(self):
        """Check that a valid SSE is recognised as such."""
        valid_sse = bytes("data: some message\n\n", encoding="utf-8")
        self.assertTrue(is_valid_sse(valid_sse))
