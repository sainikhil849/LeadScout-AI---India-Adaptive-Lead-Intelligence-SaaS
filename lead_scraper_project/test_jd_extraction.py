import asyncio
import json
from playwright.async_api import async_playwright
from scrapers.justdial_scraper import JustDialScraper

async def test_jd_profile():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # A real confirmed individual profile
        jd_url = "https://www.justdial.com/Hyderabad/Kriya-Yoga-Centre-Near-Apollo-Hospital-Jubilee-Hills/040PXX40-XX40-101103135543-A1D4_BZDET"
        print(f"Testing JustDial Profile Extraction: {jd_url}")
        
        jd = JustDialScraper()
        biz = await jd.extract_profile_data(page, jd_url)
        
        print("\n--- EXTRACTED DATA ---")
        print(json.dumps(biz, indent=2))
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_jd_profile())
