import asyncio
import logging
import re
from typing import Any, Dict, List
import pandas as pd
from playwright.async_api import async_playwright

from scrapers.google_maps_scraper import GoogleMapsScraper
from scrapers.justdial_scraper import JustDialScraper
from scrapers.sulekha_scraper import SulekhaScraper
from core.intelligence_engine import IntelligenceEngine
from core.db_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("scraper_engine")

class ScraperEngine:
    """
    Orchestrates the 2-stage deep scraping process across all enabled directories.
    """
    def __init__(self):
        self.scrapers = [
            GoogleMapsScraper(headless=False), # False to simulate real browser deeply
            JustDialScraper(headless=False),
            SulekhaScraper(headless=False)
        ]
        self.db = DatabaseManager()
        self.ai = IntelligenceEngine()

    async def _run_scraper(self, scraper, query: str, city: str, max_results: int, browser) -> List[Dict[str, Any]]:
        results = []
        name = scraper.SOURCE_NAME
        
        logger.info(f"=== Starting {name} ===")
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # ──────────────────────────────────────────
            # STAGE 1: Collect Profile URLs
            # ──────────────────────────────────────────
            logger.info(f"[{name}] Stage 1: Collecting profile URLs...")
            urls = await scraper.collect_profile_urls(page, query, city, max_results)
            logger.info(f"[{name}] Collected {len(urls)} profile URLs")
            
            # ──────────────────────────────────────────
            # STAGE 2: Dive deep into each profile
            # ──────────────────────────────────────────
            logger.info(f"[{name}] Stage 2: Extracting deep details...")
            for idx, url in enumerate(list(urls)[:max_results]):
                try:
                    biz = await scraper.extract_profile_data(page, url)
                    if biz and biz.get("name"):
                        biz["source"] = name
                        # Intelligence Processing
                        enriched_biz = self.ai.enrich_lead(biz, query)
                        
                        # Debug Verification Print
                        print(f"DEBUG PIPELINE: {enriched_biz.get('name')} | Rating: {enriched_biz.get('rating')} | Reviews: {enriched_biz.get('reviews')} | Score: {enriched_biz.get('score')}")
                        
                        # DB Persistence / Caching
                        self.db.save_lead(enriched_biz, city)
                        
                        results.append(enriched_biz)
                        rating_str = f"Score: {enriched_biz.get('score', 0)} | Priority: {enriched_biz.get('priority')}"
                        logger.info(f"[{name}] Leads: {idx+1}/{len(urls)} | {enriched_biz['name']} | {rating_str}")
                        
                    await scraper.sleep(1.0, 3.0) # Respectful delay between profiles
                except Exception as e:
                    logger.warning(f"[{name}] Failed on profile {url}: {e}")
                    
        except Exception as e:
            logger.error(f"[{name}] Scraper failed fundamentally: {e}")
        finally:
            await context.close()
            
        return results

    def _clean_data(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates."""
        cleaned = []
        seen_phones = set()
        seen_names = set()
        
        for lead in leads:
            name = lead.get("name")
            if not name:
                continue
                
            norm_name = re.sub(r"\s+", " ", name.lower().strip())
            norm_phone = lead.get("phone", "")
            
            if norm_phone:
                if norm_phone in seen_phones:
                    continue
                seen_phones.add(norm_phone)
                
            # If no phone or phone didn't trigger dedup, check name
            if norm_name in seen_names:
                continue
            seen_names.add(norm_name)
            
            cleaned.append(lead)
            
        logger.info(f"Data Cleaning: {len(leads)} raw leads -> {len(cleaned)} unique leads.")
        return cleaned

    async def execute_search(self, query: str, city: str, total_max: int = 200) -> pd.DataFrame:
        """
        Executes the full pipeline and returns a cleaned DataFrame.
        Priority: Google Maps > JustDial > Sulekha
        """
        unique_leads = []
        
        # Check Cache First to avoid redundant API/Browser logic
        cached_df = self.db.get_leads_by_category_city(query, city)
        if not cached_df.empty:
            unique_leads = cached_df.to_dict('records')
            
        remaining_quota = total_max - len(unique_leads)
        
        if remaining_quota <= 0:
            logger.info(f"Found {len(unique_leads)} cached leads. Target reached ({total_max}), skipping scrapers entirely.")
            # Return fresh from DB to ensure format consistency
            return self.db.get_leads_by_category_city(query, city).head(total_max)
        
        logger.info(f"Cache miss or partial hit: Need {remaining_quota} more leads for '{query}' in '{city}'. Warming up Playwright...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            
            for scraper in self.scrapers:
                remaining_quota = total_max - len(unique_leads)
                if remaining_quota <= 0:
                    logger.info(f"Target reached ({total_max}), skipping remaining scrapers.")
                    break
                
                try:
                    # Attempt to fill remaining quota with current scraper
                    results = await self._run_scraper(scraper, query, city, remaining_quota, browser)
                    logger.info(f"Scraper {scraper.SOURCE_NAME} returned {len(results)} results.")
                    
                    # Combine and clean to get accurate count of unique leads so far
                    temp_all = unique_leads + results
                    unique_leads = self._clean_data(temp_all)
                    
                except Exception as e:
                    logger.error(f"Error running scraper {scraper.SOURCE_NAME}: {e}")
                
            await browser.close()
            
        logger.info(f"Final pipeline count: {len(unique_leads)} unique leads.")
        return pd.DataFrame(unique_leads)
