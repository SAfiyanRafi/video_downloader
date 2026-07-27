import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional, Callable, List
from urllib.parse import urlparse

from app.models.source import MediaMetadata, SourceType
from app.services.sources.base_adapter import BaseSourceAdapter

logger = logging.getLogger("yt_splitter")

class BrowserAdapter(BaseSourceAdapter):
    """
    Automated Headless Browser Adapter using Playwright Chromium:
    Loads web pages (e.g. streaming sites), handles Cloudflare/security checks natively,
    intercepts active .m3u8 video streams and session cookies, and hands off to 16-thread downloaders.
    """

    @property
    def source_type(self) -> SourceType:
        return SourceType.WEB_PAGE

    def supports(self, source: str) -> bool:
        s = source.strip().lower()
        if not (s.startswith("http://") or s.startswith("https://")):
            return False
        # Do not hijack standard YouTube URLs or direct video files
        if "youtube.com" in s or "youtu.be" in s:
            return False
        if s.endswith(".mp4") or s.endswith(".mov") or s.endswith(".mkv") or s.endswith(".webm") or s.endswith(".mpd"):
            return False
        return True

    def validate(self, source: str) -> Tuple[bool, Optional[str]]:
        if not self.supports(source):
            return False, "Not a supported web page URL"
        return True, None

    async def probe(self, source: str) -> MediaMetadata:
        url = source.strip()
        parsed = urlparse(url)
        netloc = parsed.netloc or "webpage"
        filename = f"{netloc}_stream.mp4"
        return MediaMetadata(
            source_type=SourceType.WEB_PAGE,
            source_uri=url,
            filename=filename
        )

    async def import_media(
        self,
        source: str,
        target_dir: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        url = source.strip()
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc or "webpage"
        scheme = parsed_url.scheme or "https"

        logger.info(f"[BrowserAdapter] Launching Headless Chromium to inspect webpage: {url}")

        captured_m3u8_urls: List[str] = []
        captured_cookies = []

        try:
            import sys
            if sys.platform == "win32":
                try:
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                except Exception:
                    pass

            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080}
                )
                page = await context.new_page()

                def handle_request(req):
                    req_url = req.url
                    if ".m3u8" in req_url and req_url not in captured_m3u8_urls:
                        logger.info(f"[BrowserAdapter] Intercepted HLS stream: {req_url[:120]}")
                        captured_m3u8_urls.append(req_url)

                page.on("request", handle_request)

                logger.info(f"[BrowserAdapter] Navigating to {url}...")
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(3.0)

                captured_cookies = await context.cookies()
                await browser.close()
        except Exception as e:
            logger.warning(f"[BrowserAdapter] Playwright execution error/fallback: {e}")

        # If an HLS stream was intercepted, download via YouTubeDownloader with captured headers
        from app.services.download.youtube import YouTubeDownloader
        yt_dl = YouTubeDownloader()

        if captured_m3u8_urls:
            target_stream = captured_m3u8_urls[-1]  # Pick latest stream URL
            logger.info(f"[BrowserAdapter] Downloading intercepted stream: {target_stream}")
            try:
                dl_file = await yt_dl.download(target_stream, target_dir, progress_callback=progress_callback)
                if dl_file and dl_file.exists() and dl_file.stat().st_size > 0:
                    return dl_file
            except Exception as dl_err:
                logger.warning(f"[BrowserAdapter] Intercepted stream download failed: {dl_err}. Falling back to direct URL download...")

        # Fallback: Pass original webpage URL to yt-dlp direct extraction
        logger.info(f"[BrowserAdapter] Passing webpage URL directly to yt-dlp: {url}")
        dl_file = await yt_dl.download(url, target_dir, progress_callback=progress_callback)
        if dl_file and dl_file.exists() and dl_file.stat().st_size > 0:
            return dl_file

        raise RuntimeError(f"Failed to extract media from webpage URL: {url}")
