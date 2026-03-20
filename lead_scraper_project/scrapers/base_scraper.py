import asyncio
import random
from typing import Any, Dict, List
from playwright.async_api import Page, Playwright

class BaseScraper:
    """
    Abstract base class for all deep-extraction Playwright scrapers.
    Forces the 2-stage architecture:
      1. collect_profile_urls()
      2. extract_profile_data()
    """
    SOURCE_NAME = "base"

    def __init__(self, headless: bool = True):
        self.headless = headless

    async def sleep(self, min_s: float = 2.0, max_s: float = 5.0):
        """Random delay to avoid blocking."""
        await asyncio.sleep(random.uniform(min_s, max_s))

    async def collect_profile_urls(self, page: Page, query: str, city: str, max_results: int) -> List[str]:
        """
        Stage 1: Search and gather URLs of individual business profile pages.
        """
        raise NotImplementedError

    async def extract_profile_data(self, page: Page, url: str) -> Dict[str, Any] | None:
        """
        Stage 2: Visit the profile URL, click hidden buttons, and extract contact details.
        """
        raise NotImplementedError

    def _empty_result(self, url: str) -> Dict[str, Any]:
        return {
            "name": "",
            "phone": "",
            "email": "",
            "address": "",
            "website": "",
            "rating": None,
            "review_count": None,
            "google_maps_url": "",
            "source": self.SOURCE_NAME,
            "profile_url": url
        }
