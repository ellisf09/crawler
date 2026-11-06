import unittest

from crawl import (
    extract_page_data,
    get_first_paragraph_from_html,
    get_heading_from_html,
    get_images_from_html,
    get_urls_from_html,
    normalize_url,
)


class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_strips_https_scheme(self):
        self.assertEqual(
            normalize_url("https://www.boot.dev/blog/path"),
            "www.boot.dev/blog/path",
        )

    def test_strips_http_scheme(self):
        self.assertEqual(
            normalize_url("http://www.boot.dev/blog/path"),
            "www.boot.dev/blog/path",
        )

    def test_strips_trailing_slash(self):
        self.assertEqual(
            normalize_url("https://www.boot.dev/blog/path/"),
            "www.boot.dev/blog/path",
        )

    def test_strips_scheme_and_trailing_slash(self):
        self.assertEqual(
            normalize_url("http://www.boot.dev/blog/path/"),
            "www.boot.dev/blog/path",
        )

    def test_root_url_with_trailing_slash(self):
        self.assertEqual(normalize_url("https://www.boot.dev/"), "www.boot.dev")

    def test_root_url_without_trailing_slash(self):
        self.assertEqual(normalize_url("https://www.boot.dev"), "www.boot.dev")

    def test_lowercases_host(self):
        self.assertEqual(
            normalize_url("https://WWW.BOOT.DEV/blog/path"),
            "www.boot.dev/blog/path",
        )

    def test_lowercases_path(self):
        self.assertEqual(
            normalize_url("https://www.boot.dev/Blog/Path"),
            "www.boot.dev/blog/path",
        )

    def test_lowercases_everything(self):
        self.assertEqual(
            normalize_url("HTTPS://WWW.BOOT.DEV/Blog/Path/"),
            "www.boot.dev/blog/path",
        )

    def test_ignores_query_string(self):
        self.assertEqual(
            normalize_url("https://www.boot.dev/blog/path?page=2"),
            "www.boot.dev/blog/path",
        )

    def test_ignores_fragment(self):
        self.assertEqual(
            normalize_url("https://www.boot.dev/blog/path#section"),
            "www.boot.dev/blog/path",
        )

    def test_url_without_scheme(self):
        self.assertEqual(
            normalize_url("www.boot.dev/blog/path/"),
            "www.boot.dev/blog/path",
        )

    def test_strips_surrounding_whitespace(self):
        self.assertEqual(
            normalize_url("  https://www.boot.dev/blog/path/  "),
            "www.boot.dev/blog/path",
        )

    def test_empty_string(self):
        self.assertEqual(normalize_url(""), "")

    def test_get_heading_from_html_basic(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_prefers_h1_over_h2(self):
        input_body = "<html><body><h1>Main Title</h1><h2>Subtitle</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Main Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_h2_fallback(self):
        input_body = "<html><body><h2>Subtitle</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Subtitle"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_no_heading(self):
        input_body = "<html><body><p>Just a paragraph.</p></body></html>"
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_strips_whitespace(self):
        input_body = "<html><body><h1>  Spaced Title  </h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Spaced Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_nested_markup(self):
        input_body = "<html><body><div><h1>Title</h1></div></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_empty_html(self):
        self.assertEqual(get_heading_from_html(""), "")

    def test_get_first_paragraph_from_html_basic(self):
        input_body = "<html><body><p>Test paragraph.</p></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = "Test paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_main(self):
        input_body = """<html><body>
            <p>First paragraph.</p>
            <p>Second paragraph.</p>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "First paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_without_paragraph(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main><h1>No paragraph here</h1></main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Outside paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_paragraph(self):
        input_body = "<html><body><h1>Only a heading</h1></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_strips_whitespace(self):
        input_body = "<html><body><p>  Spaced paragraph.  </p></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = "Spaced paragraph."
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative_root(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/blog/post">Post</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/blog/post"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative_path(self):
        input_url = "https://crawler-test.com/docs/"
        input_body = '<html><body><a href="page">Page</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/docs/page"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_finds_all_anchors(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <a href="/one">One</a>
            <p>Some text with <a href="/two">Two</a> inside it.</p>
            <a href="https://example.com/three">Three</a>
        </body></html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/one",
            "https://crawler-test.com/two",
            "https://example.com/three",
        ]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_skips_anchor_without_href(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <a>No href here</a>
            <a href="/real">Real link</a>
        </body></html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/real"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_ignores_non_anchor_links(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><head>
            <link rel="stylesheet" href="/style.css">
        </head><body>
            <a href="/page">Page</a>
        </body></html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/page"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_no_anchors(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body><h1>No links here</h1></body></html>"
        actual = get_urls_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://cdn.example.com/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://cdn.example.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative_path(self):
        input_url = "https://crawler-test.com/blog/"
        input_body = '<html><body><img src="images/photo.jpg" alt="Photo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/blog/images/photo.jpg"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_finds_all_images(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <img src="/one.png" alt="One">
            <p>Text <img src="/two.png" alt="Two"></p>
            <img src="https://example.com/three.png" alt="Three">
        </body></html>"""
        actual = get_images_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/one.png",
            "https://crawler-test.com/two.png",
            "https://example.com/three.png",
        ]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_skips_image_without_src(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <img alt="No source">
            <img src="/real.png" alt="Real">
        </body></html>"""
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/real.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_no_images(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body><h1>No images here</h1></body></html>"
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_empty_html(self):
        input_url = "https://crawler-test.com/page"
        actual = extract_page_data("", input_url)
        expected = {
            "url": "https://crawler-test.com/page",
            "heading": "",
            "first_paragraph": "",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_heading_falls_back_to_h2(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h2>Subtitle</h2>
            <p>Paragraph.</p>
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        self.assertEqual(actual["heading"], "Subtitle")

    def test_extract_page_data_multiple_links_and_images(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Title</h1>
            <a href="/one">One</a>
            <a href="https://example.com/two">Two</a>
            <img src="/one.png">
            <img src="https://example.com/two.png">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        self.assertEqual(
            actual["outgoing_links"],
            ["https://crawler-test.com/one", "https://example.com/two"],
        )
        self.assertEqual(
            actual["image_urls"],
            ["https://crawler-test.com/one.png", "https://example.com/two.png"],
        )

    def test_extract_page_data_keeps_page_url_unnormalized(self):
        input_url = "https://www.crawler-test.com/Blog/Post/?page=2"
        input_body = "<html><body><h1>Title</h1></body></html>"
        actual = extract_page_data(input_body, input_url)
        self.assertEqual(actual["url"], input_url)

    def test_extract_page_data_prefers_main_paragraph(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main><p>Main paragraph.</p></main>
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        self.assertEqual(actual["first_paragraph"], "Main paragraph.")


if __name__ == "__main__":
    unittest.main()
