import asyncio
import logging
import re
from typing import Any, Dict, List
from playwright.async_api import Page, TimeoutError as PwTimeout

from scrapers.base_scraper import BaseScraper

logger = logging.getLogger("googlemaps")

class GoogleMapsScraper(BaseScraper):
    SOURCE_NAME = "google_maps"
    BASE_URL = "https://www.google.com/maps"

    async def collect_profile_urls(self, page: Page, query: str, city: str, max_results: int) -> List[str]:
        """
        Stage 1: Search Google Maps and extract profile links.
        """
        search_term = f"{query} near {city}".replace(" ", "+")
        search_url = f"{self.BASE_URL}/search/{search_term}/"

        logger.info(f"Google Maps Stage 1: Navigating to {search_url}")
        
        try:
            # Switch to domcontentloaded + manual sleep for better Maps reliability
            await page.goto(search_url, wait_until="domcontentloaded", timeout=90000)
            await self.sleep(8.0, 12.0) # Wait for listings to settle
        except Exception as e:
            logger.warning(f"Google Maps Stage 1: Load failed: {e}")
            return []

        # Wait for either results feed or specific place
        try:
            feed = page.locator('div[role="feed"]')
            await feed.wait_for(state="attached", timeout=15000)
        except PwTimeout:
            # Maybe it landed directly on a single place
            if await page.locator('h1').count() > 0:
                logger.info("Landed directly on a single Maps listing.")
                return [page.url]
            return []

        urls = []
        prev_count = 0
        scroll_attempts = (max_results // 5) + 5
        
        for _ in range(15):
            await page.mouse.move(300, 300)
            await page.mouse.wheel(0, 4000)
            await self.sleep(1.5, 2.5)
            
            listing_links = page.locator('a[href*="/maps/place/"]')
            current_count = await listing_links.count()
            if current_count >= max_results:
                break
            
            if current_count == prev_count:
                # Try a scroll up and down to shake it
                await page.mouse.wheel(0, -500)
                await self.sleep(0.5, 1.0)
                await page.mouse.wheel(0, 1000)
                
            prev_count = current_count

        # Extract profile URLs via JS for maximum reliability
        urls_list = await page.evaluate('''(max) => {
            const links = Array.from(document.querySelectorAll('a[href*="/maps/place/"]'));
            return links.map(a => a.href).slice(0, max);
        }''', max_results)
        
        for u in urls_list:
            if u not in urls:
                urls.append(u)
                
        logger.info(f"Google Maps Stage 1: Found {len(urls)} profile URLs")
        return urls

    async def extract_profile_data(self, page: Page, url: str) -> Dict[str, Any] | None:
        """
        Stage 2: Visit Google Maps listing and extract contact details.
        """
        biz = self._empty_result(url)
        biz["google_maps_url"] = url
        
        try:
            logger.info(f"Google Maps Stage 2: Visiting listing...")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await self.sleep(2.0, 4.0)
            
            # 1. Name
            name_el = page.locator('h1')
            if await name_el.count() > 0:
                biz["name"] = (await name_el.first.inner_text()).strip()
            else:
                return None
                
            # 2. Extract Phone
            # Phones in Google Maps don't require clicking 'Show', but they are inside custom buttons
            phone_btn = page.locator('button[data-item-id*="phone"]')
            if await phone_btn.count() > 0:
                label = await phone_btn.first.get_attribute("aria-label") or ""
                phone_str = label.replace("Phone:", "").strip()
                biz["phone"] = re.sub(r"[^\d+]", "", phone_str)
                
            # 3. Address
            addr_btn = page.locator('button[data-item-id="address"]')
            if await addr_btn.count() > 0:
                addr_str = await addr_btn.first.get_attribute("aria-label") or ""
                biz["address"] = addr_str.replace("Address: ", "").strip()
            
            if not biz["address"]:
                # Try JS Fallback with broader selectors
                biz["address"] = await page.evaluate(r'''() => {
                    const selectors = [
                        'button[data-item-id="address"] .Io6YTe',
                        '.fontBodyMedium',
                        '.R9Z78b',
                        'div.rogA2c',
                        '[data-tooltip="Copy address"]'
                    ];
                    for (const s of selectors) {
                        const el = document.querySelector(s);
                        if (el && el.innerText.trim()) return el.innerText.trim();
                    }
                    return '';
                }''')
                
            # 4. Website
            web_btn = page.locator('a[data-item-id="authority"]')
            if await web_btn.count() > 0:
                biz["website"] = await web_btn.first.get_attribute("href")
                
            # 5. Rating & Reviews
            # Try specific aria-label first
            rating_el = page.locator('div[role="img"][aria-label*="star"]')
            if await rating_el.count() > 0:
                label = await rating_el.first.get_attribute("aria-label") or ""
                rmatch = re.search(r"([\d.]+)\s*star", label, re.I)
                if rmatch:
                    biz["rating"] = float(rmatch.group(1))

            if biz["rating"] is None:
                # Better JS Fallback for rating/reviews
                data = await page.evaluate(r'''() => {
                    const findRating = () => {
                        const els = document.querySelectorAll('span[aria-hidden="true"], .F769Wc, .fontDisplayLarge');
                        for (const el of els) {
                            const txt = el.innerText.trim();
                            if (txt && /^\d\.\d$/.test(txt)) return txt;
                        }
                        return '';
                    };
                    const findReviews = () => {
                        const el = document.querySelector('button[aria-label*="review"], .fontBodyMedium, .jANvt');
                        return el ? el.innerText.trim() : '';
                    };
                    return {
                        rating: findRating(),
                        reviews: findReviews()
                    };
                }''')
                if data['rating']:
                    biz["rating"] = data['rating']
                if data['reviews']:
                    biz["review_count"] = data['reviews']

        except Exception as e:
            logger.debug(f"Error scraping Google Maps profile {url}: {e}")
            
        return biz
