import asyncio
import logging
import re
from typing import Any, Dict, List
from playwright.async_api import Page

from scrapers.base_scraper import BaseScraper

logger = logging.getLogger("sulekha")

class SulekhaScraper(BaseScraper):
    SOURCE_NAME = "sulekha"
    BASE_URL = "https://www.sulekha.com"

    async def collect_profile_urls(self, page: Page, query: str, city: str, max_results: int) -> List[str]:
        """
        Stage 1: Search Sulekha and extract profile links.
        """
        query_slug = query.strip().replace(" ", "+")
        city_slug = city.strip().replace(" ", "+")
        search_url = f"{self.BASE_URL}/search?q={query_slug}+in+{city_slug}"

        logger.info(f"Sulekha Stage 1: Navigating to {search_url}")
        
        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            await self.sleep(5.0, 8.0) # Sulekha is heavy on JS
        except Exception as e:
            logger.error(f"Failed to load Sulekha search page: {e}")
            return []

        urls = set()
        prev_count = 0
        
        for i in range(8):
            # Extract links to Sulekha business profiles
            # Sulekha profiles in search results usually have long specific slugs
            links = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a'))
                    .map(a => a.href)
                    .filter(href => href && href.includes('sulekha.com/') && href.length > 50);
            }''')
            
            city_l = city.lower().replace(" ", "-")
            for link in links:
                link_l = link.lower()
                # Profile links usually contain the city and ID patterns
                if city_l in link_l:
                    if not any(k in link_l for k in ["/search", "/category", "/all-cities", "/expert-listing", "collateralpolicy"]):
                        urls.add(link)
            
            if len(urls) >= max_results:
                break
                
            await page.mouse.wheel(0, 3000)
            await self.sleep(3.0, 5.0)
            
            if len(urls) == prev_count:
                break
            prev_count = len(urls)

        result_urls = list(urls)[:max_results]
        logger.info(f"Sulekha Stage 1: Found {len(result_urls)} profile URLs")
        return result_urls

    async def extract_profile_data(self, page: Page, url: str) -> Dict[str, Any] | None:
        """
        Stage 2: Visit profile, click 'Show Number', extract phone and details.
        """
        biz = self._empty_result(url)
        
        try:
            logger.info(f"Sulekha Stage 2: Visiting {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await self.sleep(3.0, 5.0)
            
            # 1. Name, Address, Rating & Reviews Extraction via JS
            data = await page.evaluate(r'''() => {
                const getName = () => {
                    const el = document.querySelector('h1, .biz-title, [itemprop="name"], .business-name, .profile-name');
                    return el ? el.innerText.trim() : '';
                };
                const getAddr = () => {
                    const el = document.querySelector('address, [itemprop="address"], .sd-address, .address, .loc-name, [itemprop="streetAddress"]');
                    return el ? el.innerText.replace(/\s+/g, ' ').trim() : '';
                };
                const getRating = () => {
                    const el = document.querySelector('span.rating-value, [itemprop="ratingValue"], .avg-rating');
                    if (!el) return '';
                    const match = el.innerText.match(/(\d+\.?\d*)/);
                    return match ? match[1] : '';
                };
                const getReviews = () => {
                    const el = document.querySelector('.review-count, [itemprop="reviewCount"], .total-reviews');
                    if (!el) return '';
                    const match = el.innerText.match(/(\d+)/);
                    return match ? match[1] : '';
                };

                return {
                    name: getName(),
                    address: getAddr(),
                    rating: getRating(),
                    reviews: getReviews()
                };
            }''')
            
            if not data['name']:
                slug = url.split('/')[-1]
                biz["name"] = " ".join(slug.split('-')[:-2]).title() or slug.replace("-", " ").title()
            else:
                biz["name"] = data['name']
            
            biz["address"] = data['address']
            biz["rating"] = float(data['rating']) if data['rating'] and data['rating'].replace('.','').isdigit() else None
            biz["review_count"] = int(data['reviews']) if data['reviews'] and data['reviews'].isdigit() else None
                
            # 2. Extract Phone by clicking button
            try:
                selectors = ["a:has-text('View Number')", "button:has-text('View Number')", ".sd-v-button", "a[href*='tel:']"]
                for sel in selectors:
                    btn = page.locator(sel)
                    if await btn.count() > 0:
                        await btn.first.click(timeout=3000, force=True)
                        await self.sleep(2.0, 3.0)
                        break
            except Exception:
                pass
            
            # 3. Phone Hunting via JS
            phones = await page.evaluate(r'''() => {
                const results = new Set();
                document.querySelectorAll('a[href^="tel:"], .sd-p-number, [itemprop="telephone"]').forEach(el => {
                    const val = el.href ? el.href.replace('tel:', '') : el.innerText;
                    results.add(val.replace(/[^\d+]/g, ''));
                });
                return Array.from(results);
            }''')
            
            valid_phones = []
            for p in phones:
                digits = re.sub(r"[^\d+]", "", p)
                if len(digits) >= 10:
                    valid_phones.append(digits)
            if valid_phones:
                biz["phone"] = ", ".join(valid_phones)
                    
        except Exception as e:
            logger.debug(f"Error scraping Sulekha profile {url}: {e}")
            
        return biz if biz.get("name") else None
