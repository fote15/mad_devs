import unittest
from bs4 import BeautifulSoup
from split_msg import split_message, MessageSplitError

class TestSplitMessage(unittest.TestCase):
    def test_simple_split(self):
        html = "<p>Hello, world!</p><p>Goodbye, world!</p>additional text"
        max_len = 22

        fragments = list(split_message(html, max_len))
        self.assertEqual(len(fragments), 3)
        self.assertEqual(fragments[0], "<p>Hello, world!</p>")
        self.assertEqual(fragments[1], "<p>Goodbye, world!</p>")
        self.assertEqual(fragments[2], "additional text")


    def test_large_message_split(self):
        html = "<div>" + "a" * 100 + "</div><div>" + "b" * 100 + "</div>"
        max_len = 150

        fragments = list(split_message(html, max_len))
        self.assertEqual(len(fragments), 2)
        self.assertEqual(len(fragments[0]), 111)  # Includes wrapping HTML tags
        self.assertEqual(len(fragments[1]), 111)

    def test_nested_html(self):
        html = "<div><p>Nested content</p><p>More content</p></div>"
        max_len = 32

        fragments = list(split_message(html, max_len))
        self.assertEqual(len(fragments), 2)
        self.assertEqual(fragments[0], "<div><p>Nested content</p></div>")
        self.assertEqual(fragments[1], "<div><p>More content</p></div>")


    def test_long_fragment_on_error(self):
        html = "<p>" + "a" * 200 + "</p>"
        max_len = 10

        with self.assertRaises(MessageSplitError):
            list(split_message(html, max_len))

    def test_html_keeping_content(self):
        html = """
            <div>
                <p>Trim this content</p>
                <p>Keep this too</p>
            </div>
        """
        max_len = 50

        fragments = list(split_message(html, max_len))
        self.assertEqual(len(fragments), 2)
        self.assertIn("<p>Trim this content</p>", fragments[0])
        self.assertIn("<p>Keep this too</p>", fragments[1])

    def test_non_html_input(self):
        html = "Plain text without HTML tags"
        max_len = 29

        fragments = list(split_message(html, max_len))
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0], "Plain text without HTML tags")

if __name__ == "__main__":
    unittest.main()
