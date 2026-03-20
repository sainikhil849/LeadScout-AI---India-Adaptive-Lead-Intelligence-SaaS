import asyncio
import logging
import re
from typing import Any, Dict, List
from playwright.async_api import Page

from scrapers.base_scraper import BaseScraper

logger = logging.getLogger("justdial")

class JustDialScraper(BaseScraper):
    SOURCE_NAME = "justdial"
    BASE_URL = "https://www.justdial.com"

    async def collect_profile_urls(self, page: Page, query: str, city: str, max_results: int) -> List[str]:
        """
        Stage 1: Search JustDial and extract profile links.
        """
        city_slug = city.strip().replace(" ", "-").capitalize()
        query_slug = query.strip().replace(" ", "-").capitalize()
        
        # Try both direct slug and Search URL
        search_urls = [
            f"{self.BASE_URL}/{city_slug}/{query_slug}",
            f"{self.BASE_URL}/{city_slug}/{query_slug}-Classes",
            f"{self.BASE_URL}/{city_slug}/Search/{query_slug}"
        ]
        
        urls = set()
        for search_url in search_urls:
            if len(urls) >= max_results:
                break
                
            logger.info(f"JustDial Stage 1: Trying {search_url}")
            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                # Fixed wait for JS to populate listings
                await self.sleep(4.0, 6.0)
                
                # Check for "Search Results" or listing containers
                link_locator = page.locator("a")
                link_count = await link_locator.count()
                
                city_l = city.lower()
                query_words = query.lower().split()
                
                for index in range(link_count):
                    try:
                        link = await link_locator.nth(index).get_attribute("href")
                        if not link or link.startswith("javascript") or "#" in link:
                            continue
                        
                        link_l = link.lower()
                        # CRITICAL FIX: Only collect individual business profiles (usually containing _BZDET)
                        # Avoid category listing pages like /nct- or /dc- unless they are confirmed profiles
                        if f"/{city_l}/" in link_l and "_bzdet" in link_l:
                            full_url = link if link.startswith("http") else f"{self.BASE_URL}{link}"
                            urls.add(full_url)
                        elif f"/{city_l}/" in link_l and not ("nct-" in link_l or "dc-" in link_l):
                            # Fallback for other potential profile patterns
                            full_url = link if link.startswith("http") else f"{self.BASE_URL}{link}"
                            urls.add(full_url)
                    except Exception:
                        continue
                            
                if len(urls) > 0:
                    # Found some, try to scroll and get more from this URL
                    for i in range(5):
                        if len(urls) >= max_results: break
                        await page.mouse.wheel(0, 3000)
                        await self.sleep(2.0, 3.0)
                        
                        # Re-extract
                        new_links = await page.evaluate('''() => {
                            return Array.from(document.querySelectorAll('a'))
                                .map(a => a.href)
                                .filter(href => href && !href.startsWith('javascript'));
                        }''')
                        
                        for l in new_links:
                            if not l: continue
                            l_l = l.lower()
                            if f"/{city_l}/" in l_l and "_bzdet" in l_l:
                                full_url = l if l.startswith("http") else f"{self.BASE_URL}{l}"
                                urls.add(full_url)

            except Exception as e:
                logger.warning(f"Failed to load search URL {search_url}: {e}")
                continue

        result_urls = list(urls)[:max_results]
        logger.info(f"JustDial Stage 1: Found {len(result_urls)} profile URLs")
        return result_urls

    async def extract_profile_data(self, page: Page, url: str) -> Dict[str, Any] | None:
        """
        Stage 2: Visit profile, click 'Show Number', extract real phone and details.
        """
        biz = self._empty_result(url)
        
        try:
            logger.info(f"JustDial Stage 2: Visiting {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await self.sleep(3.0, 5.0)
            
            # 1. Name, Address, Rating & Reviews Extraction via JS
            data = await page.evaluate(r'''() => {
                const getName = () => {
                    const el = document.querySelector('h1, .fn, .font22, .company-name, .css-175oi2r h1, #set_company_name');
                    return el ? el.innerText.trim() : '';
                };
                const getAddr = () => {
                    // Ultra-robust selectors for JustDial Address
                    const el = document.querySelector('.address-info .font15, .comp-add span, span.rct_address, address, .adr, .company-address, [itemprop="streetAddress"], .adrs, .comp-addres');
                    return el ? el.innerText.replace(/\s+/g, ' ').replace('Sort by...', '').trim() : '';
                };
                const getRating = () => {
                    const el = document.querySelector('.comp-rat .green-bx, .rating-value, .avg-rating, .rating_n, [itemprop="ratingValue"]');
                    if (!el) return '';
                    const match = el.innerText.match(/(\d+\.?\d*)/);
                    return match ? match[1] : '';
                };
                const getReviews = () => {
                    const el = document.querySelector('.comp-rat .count-reviews, .rev_cnt, [itemprop="reviewCount"], .total-reviews');
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
                match = re.search(r'/([^/]+)/nct-', url)
                biz["name"] = match.group(1).replace("-", " ").title() if match else ""
            else:
                biz["name"] = data['name']
            
            biz["address"] = data['address']
            biz["rating"] = data['rating']
            biz["review_count"] = data['reviews']
                
            # 2. Extract Phone by clicking "Show Number" button
            try:
                selectors = ["span:has-text('Show Number')", "button:has-text('Show Number')", ".tel-btn", ".callcontent"]
                for sel in selectors:
                    btn = page.locator(sel)
                    if await btn.count() > 0:
                        await btn.first.click(timeout=3000, force=True)
                        await self.sleep(1.5, 2.5)
                        break
            except Exception:
                pass
            
            # 3. Extract revealed phone numbers (Standard + JS Hunting)
            phones = await page.evaluate(r'''() => {
                const results = new Set();
                document.querySelectorAll('a[href^="tel:"]').forEach(a => {
                    results.add(a.href.replace('tel:', '').replace(/[^\d+]/g, ''));
                });
                const text = document.body.innerText;
                const matches = text.match(/(\+91|0)?[6-9]\d{9}/g);
                if (matches) matches.forEach(m => results.add(m.replace(/[^\d+]/g, '')));
                return Array.from(results);
            }''')
            
            valid_phones = []
            for p in phones:
                digits = re.sub(r"[^\d+]", "", p)
                if len(digits) >= 10:
                    valid_phones.append(digits)
            biz["phone"] = ", ".join(valid_phones) if valid_phones else ""

        except Exception as e:
            logger.debug(f"Error scraping JustDial profile {url}: {e}")
            
        return biz if biz.get("name") else None
