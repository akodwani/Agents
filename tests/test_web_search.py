import unittest

from tools.web_search import search


class WebSearchTests(unittest.TestCase):
    def test_search_fails_gracefully_when_not_configured(self) -> None:
        with self.assertRaisesRegex(NotImplementedError, "not configured"):
            search("test query")


if __name__ == "__main__":
    unittest.main()
