import asyncio
from playwright.async_api import async_playwright

async def scan():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        print("\n--- JustDial ---")
        try:
            page = await browser.new_page()
            await page.goto("https://www.justdial.com/Hyderabad/Yoga-Classes/nct-10545576", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000) # wait for js
            links = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a'))
                    .map(a => a.href)
                    .filter(h => h && h.includes('justdial.com/Hyderabad/'));
            }''')
            profiles = list(set([l for l in links if '_BZDET' in l or re.search(r'\d{4}[A-Z]{1,2}', l)]))
            print("Found links with BZDET:")
            for l in list(set([l for l in links if '_BZDET' in l]))[:10]:
                print(l)
            print("\nFirst 30 JD links:")
            for l in list(set(links))[:30]:
                print(l)
            await page.close()
        except Exception as e:
            print("JD Error:", e)

        print("\n--- Sulekha ---")
        try:
            page2 = await browser.new_page()
            await page2.goto("https://www.sulekha.com/search?q=yoga+classes+in+hyderabad", wait_until="domcontentloaded", timeout=60000)
            await page2.wait_for_timeout(5000)
            links = await page2.evaluate('''() => {
                return Array.from(document.querySelectorAll('a'))
                    .map(a => a.href)
                    .filter(h => h && h.includes('sulekha.com/'));
            }''')
            print("First 30 SK links:")
            for l in list(set(links))[:30]:
                print(l)
            await page2.close()
        except Exception as e:
            print("SK Error:", e)

        await browser.close()

if __name__ == "__main__":
    import re
    asyncio.run(scan())
