import asyncio
import logging
from core.scraper_engine import ScraperEngine

async def final_check():
    # Set logging to see our new messages
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    engine = ScraperEngine()
    # We'll just test GoogleMaps and JustDial briefly
    print("\n--- Running Final Verification Run ---")
    df = await engine.execute_search("Dance classes", "Hyderabad", total_max=3)
    
    print("\n--- FINAL AUDIT ---")
    if not df.empty:
        print(f"Total Unique Leads: {len(df)}")
        cols = ['name', 'phone', 'address', 'rating']
        available_cols = [c for c in cols if c in df.columns]
        print(df[available_cols].to_string())
    else:
        print("No leads found in this quick test.")

if __name__ == "__main__":
    asyncio.run(final_check())
