import asyncio
import logging
from playwright.async_api import async_playwright
from scrapers.justdial_scraper import JustDialScraper
from scrapers.sulekha_scraper import SulekhaScraper

logging.basicConfig(level=logging.DEBUG)

async def test_scrapers():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("\n--- Testing JustDial ---")
        jd = JustDialScraper(headless=False)
        jd_urls = await jd.collect_profile_urls(page, "Yoga", "Hyderabad", 10)
        # with open("jd.html", "w", encoding="utf-8") as f:
        #     f.write(await page.content())
        print(f"JustDial URL count: {len(jd_urls)}")
        if jd_urls:
            print(f"Sample JD URL: {jd_urls[0]}")
            jd_data = await jd.extract_profile_data(page, jd_urls[0])
            print(f"JD Data Full: {jd_data}")
            
        print("\n--- Testing Sulekha ---")
        sk = SulekhaScraper(headless=False)
        sk_urls = await sk.collect_profile_urls(page, "Yoga", "Hyderabad", 10)
        # with open("sk.html", "w", encoding="utf-8") as f:
        #     f.write(await page.content())
        print(f"Sulekha URL count: {len(sk_urls)}")
        if sk_urls:
            print(f"Sample SK URL: {sk_urls[0]}")
            sk_data = await sk.extract_profile_data(page, sk_urls[0])
            print(f"SK Data Full: {sk_data}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_scrapers())
