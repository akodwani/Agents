"""Polite HTTP layer: robots.txt, per-host rate limiting, retries, caching.

Only publicly accessible pages are requested. Nothing here attempts to defeat
CAPTCHAs, authentication, paywalls or anti-bot systems: a 401/403/429 is
recorded as an inaccessible source and the crawl moves on.
"""

from __future__ import annotations

import random
import time
import urllib.robotparser as robotparser
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 jobhunt/1.0 "
      "(personal job search; contact: local user)")

CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "cache"
MIN_DELAY = 1.5           # seconds between requests to the same host
BLOCK_STATUSES = {401, 402, 403, 407, 429}


@dataclass
class Response:
    url: str
    status: int
    text: str
    ok: bool
    reason: str = ""
    final_url: str = ""

    @property
    def blocked(self) -> bool:
        return self.status in BLOCK_STATUSES or self.reason.startswith("robots")


class Fetcher:
    def __init__(self, respect_robots: bool = True, delay: float = MIN_DELAY,
                 timeout: int = 25, cache: bool = True, default_retries: int = 2):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.respect_robots = respect_robots
        self.delay = delay
        self.timeout = timeout
        self.cache = cache
        self.default_retries = default_retries
        self._last: dict[str, float] = {}
        self._robots: dict[str, robotparser.RobotFileParser | None] = {}
        self.host_status: dict[str, str] = {}
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------ robots --
    def _robot(self, url: str) -> robotparser.RobotFileParser | None:
        host = urlparse(url).netloc
        if host in self._robots:
            return self._robots[host]
        rp = robotparser.RobotFileParser()
        rp.set_url(f"{urlparse(url).scheme}://{host}/robots.txt")
        try:
            self._throttle(host)
            r = self.session.get(rp.url, timeout=self.timeout)
            if r.status_code == 200:
                rp.parse(r.text.splitlines())
            else:
                rp = None                      # no robots.txt => allowed
        except requests.RequestException:
            rp = None
        self._robots[host] = rp
        return rp

    def allowed(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        rp = self._robot(url)
        if rp is None:
            return True
        try:
            return rp.can_fetch(UA, url)
        except Exception:
            return True

    # ---------------------------------------------------------- throttle --
    def _throttle(self, host: str) -> None:
        last = self._last.get(host)
        if last is not None:
            wait = self.delay + random.uniform(0, 0.6) - (time.time() - last)
            if wait > 0:
                time.sleep(wait)
        self._last[host] = time.time()

    # --------------------------------------------------------------- get --
    def get(self, url: str, retries: int | None = None, json_expected: bool = False) -> Response:
        if retries is None:
            retries = self.default_retries
        host = urlparse(url).netloc
        if not self.allowed(url):
            self.host_status[host] = "blocked_robots"
            return Response(url, 0, "", False, "robots.txt disallows this path")

        cache_file = CACHE_DIR / f"{abs(hash(url))}.html"
        if self.cache and cache_file.exists() and time.time() - cache_file.stat().st_mtime < 6 * 3600:
            return Response(url, 200, cache_file.read_text(errors="ignore"), True, "cache")

        backoff = 2.0
        for attempt in range(retries + 1):
            self._throttle(host)
            try:
                r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            except requests.RequestException as exc:
                if attempt == retries:
                    self.host_status[host] = "network_error"
                    return Response(url, 0, "", False, f"network: {type(exc).__name__}: {exc}")
                time.sleep(backoff)
                backoff *= 2
                continue

            if r.status_code in BLOCK_STATUSES:
                self.host_status[host] = "blocked_network"
                return Response(url, r.status_code, "", False,
                                f"blocked with HTTP {r.status_code}; not retried", r.url)
            if r.status_code >= 500 and attempt < retries:
                time.sleep(backoff)
                backoff *= 2
                continue

            ok = r.status_code == 200
            if ok and self.cache:
                try:
                    cache_file.write_text(r.text)
                except OSError:
                    pass
            self.host_status[host] = "ok" if ok else f"http_{r.status_code}"
            return Response(url, r.status_code, r.text if ok else "", ok, "", r.url)
        return Response(url, 0, "", False, "exhausted retries")

    def get_json(self, url: str):
        r = self.get(url, json_expected=True)
        if not r.ok:
            return None, r
        import json
        try:
            return json.loads(r.text), r
        except ValueError:
            return None, Response(url, r.status, "", False, "not json")


_default: Fetcher | None = None


def default_fetcher() -> Fetcher:
    global _default
    if _default is None:
        _default = Fetcher()
    return _default
