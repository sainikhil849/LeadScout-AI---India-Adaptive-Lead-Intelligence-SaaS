import asyncio
import json
from playwright.async_api import async_playwright
from scrapers.google_maps_scraper import GoogleMapsScraper

async def test_single_map():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # A real confirmed individual profile with address and rating
        url = "https://www.google.com/maps/place/Kriya+Yoga+Centre/@17.4204558,78.4116962,17z/data=!3m1!4b1!4m6!3m5!1s0x3bcb9729f285f7fd:0xb63493881c1955b2!8m2!3d17.4204558!4d78.4116962"
        print(f"Testing Google Maps Extraction: {url}")
        
        gm = GoogleMapsScraper()
        biz = await gm.extract_profile_data(page, url)
        
        print("\n--- EXTRACTED DATA ---")
        print(json.dumps(biz, indent=2))
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_single_map())
