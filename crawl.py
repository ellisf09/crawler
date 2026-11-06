import asyncio
from typing import TypedDict
from urllib.parse import urljoin, urlsplit

import aiohttp
from bs4 import BeautifulSoup, Tag


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def normalize_url(url: str) -> str:
    """Return a canonical form of a URL, so equivalent URLs compare equal.

    The scheme, query string and fragment are dropped, the host and path are
    lowercased, and any trailing slash is removed.
    """
    parsed = urlsplit(url.strip())

    if not parsed.netloc:
        return parsed.path.lower().rstrip("/")

    netloc = parsed.netloc.lower()
    path = parsed.path.lower().rstrip("/")
    return netloc + path


def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find("h1") or soup.find("h2")
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""


def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main_tag = soup.find("main")
    if isinstance(main_tag, Tag):
        p_tag = main_tag.find("p")
        if isinstance(p_tag, Tag):
            return p_tag.get_text(strip=True)
    p_tag = soup.find("p")
    return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""


def get_urls_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for a_tag in soup.find_all("a"):
        href = a_tag.get("href")
        if isinstance(href, str) and href:
            urls.append(urljoin(base_url, href))
    return urls


def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        if isinstance(src, str) and src:
            urls.append(urljoin(base_url, src))
    return urls


def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }


class AsyncCrawler:
    def __init__(
        self, base_url: str, max_concurrency: int = 5, max_pages: int = 100
    ):
        self.base_url = base_url
        self.base_domain = urlsplit(base_url).netloc.lower()
        self.page_data: dict[str, PageData] = {}
        self.visited: set[str] = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.max_pages = max_pages
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session: aiohttp.ClientSession | None = None
        self.should_stop = False
        self.all_tasks: set[asyncio.Task[None]] = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session is not None:
            await self.session.close()

    async def add_page_visit(self, normalized_url: str) -> bool:
        async with self.lock:
            if self.should_stop:
                return False
            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                return False
            if normalized_url in self.visited:
                return False
            self.visited.add(normalized_url)
            return True

    async def get_html(self, url: str) -> str:
        if self.session is None:
            raise RuntimeError("session is not open, use 'async with AsyncCrawler(...)'")

        async with self.session.get(
            url, headers={"User-Agent": "BootCrawler/1.0"}
        ) as response:
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            mime_type = content_type.split(";")[0].strip().lower()
            if mime_type != "text/html":
                raise ValueError(
                    f"expected text/html, got content-type: {content_type!r}"
                )

            return await response.text()

    async def crawl_page(self, current_url: str) -> None:
        if self.should_stop:
            return

        if urlsplit(current_url).netloc.lower() != self.base_domain:
            return

        normalized_url = normalize_url(current_url)
        if not await self.add_page_visit(normalized_url):
            return

        async with self.semaphore:
            print(f"crawling: {current_url}")
            try:
                html = await self.get_html(current_url)
            except Exception as e:
                print(f"error crawling {current_url}: {e}")
                return

            data = extract_page_data(html, current_url)
            async with self.lock:
                self.page_data[normalized_url] = data

        tasks = []
        for link in data["outgoing_links"]:
            if self.should_stop:
                break
            task = asyncio.create_task(self._crawl_tracked(link))
            self.all_tasks.add(task)
            tasks.append(task)
        if tasks:
            await asyncio.gather(*tasks)

    async def _crawl_tracked(self, url: str) -> None:
        task = asyncio.current_task()
        try:
            await self.crawl_page(url)
        finally:
            if task is not None:
                self.all_tasks.discard(task)

    async def crawl(self) -> dict[str, PageData]:
        await self.crawl_page(self.base_url)
        return self.page_data


async def crawl_site_async(
    base_url: str, max_concurrency: int = 5, max_pages: int = 100
) -> dict[str, PageData]:
    async with AsyncCrawler(
        base_url, max_concurrency=max_concurrency, max_pages=max_pages
    ) as crawler:
        return await crawler.crawl()
