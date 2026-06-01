import time
import unittest
from unittest.mock import MagicMock

from aider.commands import Commands
from aider.io import InputOutput
from aider.scrape import Scraper


class TestScrape(unittest.TestCase):
    def test_scrape_self_signed_ssl(self):
        def scrape_with_retries(scraper, url, max_retries=5, delay=0.5):
            for _ in range(max_retries):
                result = scraper.scrape(url)
                if result is not None:
                    return result
                time.sleep(delay)
            return None

        # Test with SSL verification
        scraper_verify = Scraper(
            print_error=MagicMock(), playwright_available=True, verify_ssl=True
        )
        result_verify = scrape_with_retries(scraper_verify, "https://self-signed.badssl.com")
        self.assertIsNone(result_verify)
        scraper_verify.print_error.assert_called()

        # Test without SSL verification
        scraper_no_verify = Scraper(
            print_error=MagicMock(), playwright_available=True, verify_ssl=False
        )
        result_no_verify = scrape_with_retries(scraper_no_verify, "https://self-signed.badssl.com")
        self.assertIsNotNone(result_no_verify)
        self.assertIn("self-signed", result_no_verify)
        scraper_no_verify.print_error.assert_not_called()

    def setUp(self):
        self.io = InputOutput(yes=True)
        self.commands = Commands(self.io, None)

    def test_cmd_web_imports_playwright(self):
        # Create a mock print_error function
        mock_print_error = MagicMock()
        self.commands.io.tool_error = mock_print_error

        # Run the cmd_web command
        result = self.commands.cmd_web("https://example.com", return_content=True)

        # Assert that the result contains some content
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "")

        # Try to import playwright
        try:
            import playwright  # noqa: F401

            playwright_imported = True
        except ImportError:
            playwright_imported = False

        # Assert that playwright was successfully imported
        self.assertTrue(
            playwright_imported, "Playwright should be importable after running cmd_web"
        )

        # Assert that print_error was never called
        mock_print_error.assert_not_called()

    def test_scrape_actual_url_with_playwright(self):
        # Create a Scraper instance with a mock print_error function
        mock_print_error = MagicMock()
        scraper = Scraper(print_error=mock_print_error, playwright_available=True)

        # Scrape a real URL
        result = scraper.scrape("https://example.com")

        # Assert that the result contains expected content
        self.assertIsNotNone(result)
        self.assertIn("Example Domain", result)

        # Assert that print_error was never called
        mock_print_error.assert_not_called()

    def test_scraper_print_error_not_called(self):
        # Create a Scraper instance with a mock print_error function
        mock_print_error = MagicMock()
        scraper = Scraper(print_error=mock_print_error, verify_ssl=False)

        # Test various methods of the Scraper class
        scraper.scrape_with_httpx("https://example.com")
        scraper.try_pandoc()
        scraper.html_to_markdown("<html><body><h1>Test</h1></body></html>")

        # Assert that print_error was never called
        mock_print_error.assert_not_called()

    def test_scrape_with_playwright_error_handling(self):
        # Create a Scraper instance with a mock print_error function
        mock_print_error = MagicMock()
        scraper = Scraper(print_error=mock_print_error, playwright_available=True)

        # Mock the playwright module to raise an error
        import playwright

        playwright._impl._errors.Error = Exception  # Mock the Error class

        def mock_content():
            raise playwright._impl._errors.Error("Test error")

        # Mock the necessary objects and methods
        scraper.scrape_with_playwright = MagicMock()
        scraper.scrape_with_playwright.return_value = (None, None)

        # Call the scrape method
        result = scraper.scrape("https://example.com")

        # Assert that the result is None
        self.assertIsNone(result)

        # Assert that print_error was called with the expected error message
        mock_print_error.assert_called_once_with(
            "Failed to retrieve content from https://example.com"
        )

        # Reset the mock
        mock_print_error.reset_mock()

        # Test with a different return value
        scraper.scrape_with_playwright.return_value = ("Some content", "text/html")
        result = scraper.scrape("https://example.com")

        # Assert that the result is not None
        self.assertIsNotNone(result)

        # Assert that print_error was not called
        mock_print_error.assert_not_called()

    def test_scrape_text_plain(self):
        # Create a Scraper instance
        scraper = Scraper(print_error=MagicMock(), playwright_available=True)

        # Mock the scrape_with_playwright method
        plain_text = "This is plain text content."
        scraper.scrape_with_playwright = MagicMock(return_value=(plain_text, "text/plain"))

        # Call the scrape method
        result = scraper.scrape("https://example.com")

        # Assert that the result is the same as the input plain text
        self.assertEqual(result, plain_text)

    def test_scrape_text_html(self):
        # Create a Scraper instance
        scraper = Scraper(print_error=MagicMock(), playwright_available=True)

        # Mock the scrape_with_playwright method
        html_content = "<html><body><h1>Test</h1><p>This is HTML content.</p></body></html>"
        scraper.scrape_with_playwright = MagicMock(return_value=(html_content, "text/html"))

        # Mock the html_to_markdown method
        expected_markdown = "# Test\n\nThis is HTML content."
        scraper.html_to_markdown = MagicMock(return_value=expected_markdown)

        # Call the scrape method
        result = scraper.scrape("https://example.com")

        # Assert that the result is the expected markdown
        self.assertEqual(result, expected_markdown)

        # Assert that html_to_markdown was called with the HTML content
        scraper.html_to_markdown.assert_called_once_with(html_content)


class TestParseLlmsTxtSkills(unittest.TestCase):
    def test_parses_skills_section(self):
        from aider.scrape import parse_llms_txt_skills

        text = (
            "# Some API\n\n"
            "> tagline\n\n"
            "## Endpoint\n\n"
            "`GET /thing`\n\n"
            "## Skills\n\n"
            "Intro prose that should be ignored.\n\n"
            "- [placeholder](/skills/placeholder/SKILL.md): make placeholder images."
            ' <!-- skill: {"version":"1.0.0"} -->\n'
            "- [api-client](/skills/api-client/SKILL.md): call the API over HTTP.\n\n"
            "## After\n\n"
            "- [not-a-skill](/x): should be ignored, wrong section.\n"
        )
        skills = parse_llms_txt_skills(text)
        self.assertEqual(
            skills,
            [
                (
                    "placeholder",
                    "/skills/placeholder/SKILL.md",
                    "make placeholder images.",
                ),
                ("api-client", "/skills/api-client/SKILL.md", "call the API over HTTP."),
            ],
        )

    def test_no_skills_section(self):
        from aider.scrape import parse_llms_txt_skills

        self.assertEqual(parse_llms_txt_skills("# Title\n\n> tag\n\n## Endpoint\n"), [])

    def test_fetch_llms_txt_rejects_html(self):
        from unittest.mock import patch

        from aider.scrape import fetch_llms_txt

        response = MagicMock()
        response.status_code = 200
        response.headers = {"content-type": "text/html; charset=utf-8"}
        response.text = "<!doctype html><html><body>SPA</body></html>"

        client = MagicMock()
        client.get.return_value = response
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)

        with patch("httpx.Client", return_value=client):
            self.assertIsNone(fetch_llms_txt("https://example.com"))

    def test_fetch_llms_txt_returns_markdown(self):
        from unittest.mock import patch

        from aider.scrape import fetch_llms_txt

        response = MagicMock()
        response.status_code = 200
        response.headers = {"content-type": "text/plain; charset=utf-8"}
        response.text = "# Site\n\n## Skills\n\n- [s](/s/SKILL.md): a skill.\n"

        client = MagicMock()
        client.get.return_value = response
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)

        with patch("httpx.Client", return_value=client):
            text = fetch_llms_txt("https://example.com")
        self.assertIsNotNone(text)
        self.assertIn("## Skills", text)


if __name__ == "__main__":
    unittest.main()
