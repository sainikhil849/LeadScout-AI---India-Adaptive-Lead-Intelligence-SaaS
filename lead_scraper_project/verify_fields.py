import asyncio
import json
from playwright.async_api import async_playwright
from scrapers.justdial_scraper import JustDialScraper
from scrapers.sulekha_scraper import SulekhaScraper
from scrapers.google_maps_scraper import GoogleMapsScraper

async def test_fields():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Test JustDial Profile
        jd_url = "https://www.justdial.com/Hyderabad/Kriya-Yoga-Centre-Near-Apollo-Hospital-Jubilee-Hills/040PXX40-XX40-101103135543-A1D4_BZDET"
        print(f"\n--- Testing JustDial: {jd_url} ---")
        jd = JustDialScraper()
        biz_jd = await jd.extract_profile_data(page, jd_url)
        print("Result:", json.dumps(biz_jd, indent=2))

        # 2. Test Google Maps Profile
        # Find a real yoga studio in Hyderabad on Maps
        gm_url = "https://www.google.com/maps/place/Kriya+Yoga+Centre/@17.4204558,78.4116962,17z/data=!3m1!4b1!4m6!3m5!1s0x3bcb9729f285f7fd:0xb63493881c1955b2!8m2!3d17.4204558!4d78.4116962!16s%2Fg%2F1tcxml8r"
        print(f"\n--- Testing Google Maps: {gm_url} ---")
        gm = GoogleMapsScraper()
        biz_gm = await gm.extract_profile_data(page, gm_url)
        print("Result:", json.dumps(biz_gm, indent=2))

        # 3. Test Sulekha Profile
        print("\n--- Testing Sulekha Search -> Profile ---")
        sk = SulekhaScraper()
        urls = await sk.collect_profile_urls(page, "Yoga", "Hyderabad", 1)
        if urls:
            print(f"Testing Sulekha Profile: {urls[0]}")
            biz_sk = await sk.extract_profile_data(page, urls[0])
            print("Result:", json.dumps(biz_sk, indent=2))
        else:
            print("No Sulekha profiles found to test.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_fields())
