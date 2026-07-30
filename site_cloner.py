import argparse
import asyncio
import http.server
import os
import re
import socketserver
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
import requests
from playwright.async_api import async_playwright

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

HEADERS = {"User-Agent": DEFAULT_USER_AGENT}


class WebCloner:
    def __init__(self, target_url: str, output_dir: str = "cloned_site", max_depth: int = 3):
        self.target_url = target_url
        self.parsed_target = urllib.parse.urlparse(target_url)
        self.domain = self.parsed_target.netloc
        self.base_url = f"{self.parsed_target.scheme}://{self.domain}"
        self.output_dir = Path(output_dir).resolve()
        self.max_depth = max_depth
        self.visited_urls = set()
        self.downloaded_assets = set()

    def _sanitize_path(self, url_path: str, default_filename: str = "index.html") -> Path:
        parsed_path = urllib.parse.urlparse(url_path).path.lstrip("/")
        if not parsed_path:
            return Path(default_filename)
        if parsed_path.endswith("/") or not os.path.splitext(parsed_path)[1]:
            return Path(parsed_path) / default_filename
        return Path(parsed_path)

    def _get_relative_prefix(self, file_path: Path) -> str:
        depth = len(file_path.parents) - 1
        return "../" * depth if depth > 0 else "./"

    def download_asset(self, asset_url: str) -> str:
        if not asset_url or asset_url.startswith(("data:", "javascript:", "mailto:", "tel:", "#")):
            return asset_url

        full_asset_url = urllib.parse.urljoin(self.target_url, asset_url)
        parsed_asset = urllib.parse.urlparse(full_asset_url)

        # Allow assets from CDNs or target domain
        local_rel_path = self._sanitize_path(parsed_asset.path)
        local_full_path = self.output_dir / local_rel_path

        if str(local_full_path) in self.downloaded_assets:
            return str(local_rel_path).replace("\\", "/")

        try:
            local_full_path.parent.mkdir(parents=True, exist_ok=True)
            response = requests.get(full_asset_url, headers=HEADERS, timeout=15)
            
            if response.status_code == 200:
                with open(local_full_path, "wb") as f:
                    f.write(response.content)
                self.downloaded_assets.add(str(local_full_path))
                print(f"  [?] Downloaded: {local_rel_path}")

                if local_full_path.suffix == ".css":
                    self._process_css_file(local_full_path, full_asset_url)

                return str(local_rel_path).replace("\\", "/")
            else:
                return asset_url
        except Exception:
            return asset_url

    def _process_css_file(self, css_path: Path, css_url: str):
        try:
            with open(css_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            url_pattern = re.compile(r'url\(([\'"]?)(.*?)\1\)')

            def replace_css_url(match):
                quote = match.group(1)
                inner_url = match.group(2).strip()
                if inner_url.startswith(("data:", "http://", "https://", "//")):
                    target = inner_url
                else:
                    target = urllib.parse.urljoin(css_url, inner_url)
                
                downloaded_path = self.download_asset(target)
                return f'url({quote}{downloaded_path}{quote})'

            updated_content = url_pattern.sub(replace_css_url, content)

            with open(css_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
        except Exception:
            pass

    async def fetch_dynamic_dom(self, page, url: str) -> str:
        print(f"\n[+] Processing: {url}")
        await page.goto(url, wait_until="networkidle", timeout=60000)

        # Auto scroll to trigger dynamic images/animations
        await page.evaluate("""
            async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    const distance = 300;
                    const timer = setInterval(() => {
                        const scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if (totalHeight >= scrollHeight) {
                            clearInterval(timer);
                            window.scrollTo(0, 0);
                            resolve();
                        }
                    }, 100);
                });
            }
        """)
        await page.wait_for_timeout(1500)
        return await page.content()

    async def clone_page(self, page, url: str, current_depth: int = 1):
        normalized_url = url.split("#")[0].rstrip("/")
        if normalized_url in self.visited_urls or current_depth > self.max_depth:
            return

        self.visited_urls.add(normalized_url)

        try:
            html_content = await self.fetch_dynamic_dom(page, url)
        except Exception as e:
            print(f"[!] Page load failed ({url}): {e}")
            return

        soup = BeautifulSoup(html_content, "html.parser")
        parsed_page = urllib.parse.urlparse(url)
        file_rel_path = self._sanitize_path(parsed_page.path)
        rel_prefix = self._get_relative_prefix(file_rel_path)

        # Download Images
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src:
                local_asset = self.download_asset(urllib.parse.urljoin(url, src))
                img["src"] = rel_prefix + local_asset
                if img.has_attr("srcset"):
                    del img["srcset"]

        # Download Stylesheets
        for link in soup.find_all("link", rel=lambda x: x and "stylesheet" in x.lower()):
            href = link.get("href")
            if href:
                local_asset = self.download_asset(urllib.parse.urljoin(url, href))
                link["href"] = rel_prefix + local_asset

        # Download Scripts
        for script in soup.find_all("script", src=True):
            src = script.get("src")
            if src:
                local_asset = self.download_asset(urllib.parse.urljoin(url, src))
                script["src"] = rel_prefix + local_asset

        # Collect internal links for deep recursion
        internal_links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue

            full_link = urllib.parse.urljoin(url, href)
            parsed_link = urllib.parse.urlparse(full_link)

            if parsed_link.netloc == self.domain:
                target_rel_path = self._sanitize_path(parsed_link.path)
                local_href = rel_prefix + str(target_rel_path).replace("\\", "/")
                if parsed_link.fragment:
                    local_href += f"#{parsed_link.fragment}"
                a_tag["href"] = local_href
                internal_links.append(full_link)

        # Save HTML page
        save_path = self.output_dir / file_rel_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        print(f"[?] Saved page: {file_rel_path}")

        # Recurse through internal pages
        if current_depth < self.max_depth:
            for link in internal_links:
                await self.clone_page(page, link, current_depth + 1)

    async def run(self):
        print(f"==================================================")
        print(f"  Target URL : {self.target_url}")
        print(f"  Max Depth  : {self.max_depth}")
        print(f"  Output Dir : {self.output_dir}")
        print(f"==================================================")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=DEFAULT_USER_AGENT,
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            await self.clone_page(page, self.target_url, current_depth=1)
            await browser.close()

        print(f"\n[+] Completed! Total pages crawled: {len(self.visited_urls)}")


def serve_directory(directory: Path, port: int = 8000):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n[+] Serving entire local site at: http://localhost:{port}")
        print("[+] Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[-] Server stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full Multi-Page Website Cloner")
    parser.add_argument("url", help="Target URL to clone")
    parser.add_argument("-o", "--output", default="cloned_site", help="Output directory")
    parser.add_argument("-d", "--depth", type=int, default=3, help="Crawl depth (default 3)")
    parser.add_argument("-s", "--serve", action="store_true", help="Serve site after clone")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Server port")

    args = parser.parse_args()

    cloner = WebCloner(target_url=args.url, output_dir=args.output, max_depth=args.depth)
    asyncio.run(cloner.run())

    if args.serve:
        serve_directory(cloner.output_dir, port=args.port)
