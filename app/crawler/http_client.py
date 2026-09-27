from __future__ import annotations

import hashlib
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from app.config import settings


@dataclass
class FetchResult:
    url: str
    status_code: int | None
    content: bytes | None
    content_hash: str | None
    title: str | None
    robots_allowed: bool | None
    error_message: str | None
    fetched_at: datetime


class RateLimiter:
    def __init__(self, delay: float, max_per_minute: int):
        self.delay = delay
        self.max_per_minute = max_per_minute
        self._last: dict[str, float] = {}
        self._window: dict[str, deque[float]] = defaultdict(deque)

    def wait(self, domain: str) -> None:
        now = time.time()
        last = self._last.get(domain, 0)
        sleep_for = self.delay - (now - last)
        if sleep_for > 0:
            time.sleep(sleep_for)
        window = self._window[domain]
        cutoff = time.time() - 60
        while window and window[0] < cutoff:
            window.popleft()
        if len(window) >= self.max_per_minute:
            time.sleep(max(0.1, 60 - (time.time() - window[0])))
        self._last[domain] = time.time()
        self._window[domain].append(self._last[domain])


class HttpCrawler:
    """Kamuya açık sayfalar için kontrollü indirici. Oturum/CAPTCHA yok."""

    def __init__(self):
        self.limiter = RateLimiter(
            settings.request_delay_seconds,
            settings.max_requests_per_domain_per_minute,
        )
        self._robots: dict[str, RobotFileParser | None] = {}
        self.client = httpx.Client(
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
            timeout=30.0,
        )

    def close(self) -> None:
        self.client.close()

    def robots_allowed(self, url: str) -> bool:
        if not settings.respect_robots_txt:
            return True
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._robots:
            rp = RobotFileParser()
            robots_url = origin + "/robots.txt"
            try:
                self.limiter.wait(parsed.netloc)
                resp = self.client.get(robots_url)
                if resp.status_code >= 400:
                    self._robots[origin] = None
                else:
                    rp.parse(resp.text.splitlines())
                    self._robots[origin] = rp
            except httpx.HTTPError:
                self._robots[origin] = None
        rp = self._robots[origin]
        if rp is None:
            return True
        return rp.can_fetch(settings.user_agent, url)

    def fetch(self, url: str) -> FetchResult:
        parsed = urlparse(url)
        allowed = self.robots_allowed(url)
        if not allowed:
            return FetchResult(
                url=url,
                status_code=None,
                content=None,
                content_hash=None,
                title=None,
                robots_allowed=False,
                error_message="robots.txt disallowed",
                fetched_at=datetime.utcnow(),
            )
        try:
            self.limiter.wait(parsed.netloc)
            resp = self.client.get(url)
            body = resp.content
            digest = hashlib.sha256(body).hexdigest()
            title = None
            if "html" in resp.headers.get("content-type", "").lower() or body[:200].lower().find(b"<html") != -1:
                soup = BeautifulSoup(body, "lxml")
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()[:500]
            path = settings.snapshot_dir / f"{digest[:16]}.bin"
            if not path.exists():
                path.write_bytes(body)
            return FetchResult(
                url=str(resp.url),
                status_code=resp.status_code,
                content=body,
                content_hash=digest,
                title=title,
                robots_allowed=True,
                error_message=None if resp.status_code < 400 else f"HTTP {resp.status_code}",
                fetched_at=datetime.utcnow(),
            )
        except httpx.HTTPError as exc:
            return FetchResult(
                url=url,
                status_code=None,
                content=None,
                content_hash=None,
                title=None,
                robots_allowed=True,
                error_message=str(exc),
                fetched_at=datetime.utcnow(),
            )


def snapshot_path(content_hash: str) -> Path:
    return settings.snapshot_dir / f"{content_hash[:16]}.bin"
