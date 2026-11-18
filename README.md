# Web Crawler

![GitHub License](https://img.shields.io/github/license/ellisf09/crawler)
![GitHub last commit](https://img.shields.io/github/last-commit/ellisf09/crawler)

<img src="https://skillicons.dev/icons?i=py">

An asynchronous/recursive CLI web crawler built in Python that maps internal website links and exports structured crawl data to JSON.

## ✨ Features
- **Internal Link Discovery:** Parses HTML documents to extract and normalise anchor links within a target domain.
- **Frequency Tracking:** Counts internal page references across the site structure.
- **JSON Reporting:** Exports clean, structured crawl summaries via `json_report.py`.

## 🚀 Installation & Usage
This project uses `uv` for dependency and environment management.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ellisf09/crawler
   cd crawler
   ```
2. **Sync dependencies:**
   ```bash
   uv sync
   ```
3. **Run the crawler:**
   ```bash
   uv run main.py <BASE_URL>
   ```
4. **Run unit tests:**
   ```bash
   uv run pytest
   ```
