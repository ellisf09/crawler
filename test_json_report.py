import json
import os
import tempfile
import unittest

from json_report import write_json_report


def make_page(url: str) -> dict:
    return {
        "url": url,
        "heading": "Heading",
        "first_paragraph": "Paragraph.",
        "outgoing_links": [],
        "image_urls": [],
    }


class TestJSONReport(unittest.TestCase):
    def test_writes_sorted_json_array(self):
        page_data = {
            "crawler-test.com/b": make_page("https://crawler-test.com/b"),
            "crawler-test.com/a": make_page("https://crawler-test.com/a"),
            "crawler-test.com/c": make_page("https://crawler-test.com/c"),
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "report.json")
            write_json_report(page_data, path)

            with open(path, encoding="utf-8") as f:
                report = json.load(f)

        self.assertIsInstance(report, list)
        self.assertEqual(
            [page["url"] for page in report],
            [
                "https://crawler-test.com/a",
                "https://crawler-test.com/b",
                "https://crawler-test.com/c",
            ],
        )

    def test_default_filename(self):
        page_data = {"crawler-test.com": make_page("https://crawler-test.com")}
        original_cwd = os.getcwd()

        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                os.chdir(tmp_dir)
                write_json_report(page_data)
                self.assertTrue(os.path.exists("report.json"))
                with open("report.json", encoding="utf-8") as f:
                    report = json.load(f)
            finally:
                os.chdir(original_cwd)

        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["url"], "https://crawler-test.com")


if __name__ == "__main__":
    unittest.main()
