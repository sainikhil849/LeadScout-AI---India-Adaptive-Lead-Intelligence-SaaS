import asyncio
import logging
from core.scraper_engine import ScraperEngine

logging.basicConfig(level=logging.INFO)

async def main():
    engine = ScraperEngine()
    print("Welcome to Deep LeadScout AI CLI")
    query = input("Category: ")
    city = input("City: ")
    max_res = int(input("Max results: "))
    
    try:
        df = await engine.execute_search(query, city, max_res)
        print(f"\nScraping complete. Found {len(df)} leads.")
        if not df.empty:
            filename = f"leads_{query.replace(' ', '_')}_{city}.xlsx"
            df.to_excel(filename, index=False)
            print(f"Data saved to {filename}")
        else:
            print("No leads found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
