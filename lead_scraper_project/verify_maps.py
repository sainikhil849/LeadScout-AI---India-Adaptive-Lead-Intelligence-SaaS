import asyncio
import os
import pandas as pd
from core.scraper_engine import ScraperEngine

async def test_maps_priority():
    print("\n--- GOOGLE MAPS PRIORITY TEST ---")
    engine = ScraperEngine()
    
    # We'll run a small search for 5 results
    query = "Dance classes"
    city = "Hyderabad"
    
    # Execute search
    df = await engine.execute_search(query, city, total_max=10)
    
    if not df.empty:
        print(f"\n✅ Found {len(df)} leads.")
        print("\nAudit of extracted fields:")
        fields = ['name', 'phone', 'address', 'rating']
        for col in fields:
            if col in df.columns:
                filled = df[col].notna().sum()
                print(f" - {col}: {filled}/{len(df)} ({(filled/len(df))*100:.1f}%)")
        
        print("\nTop 5 Results Sample:")
        pd.set_option('display.max_colwidth', 50)
        print(df[fields].head(5).to_string())
    else:
        print("\n❌ No results found. Check logs for details.")

if __name__ == "__main__":
    asyncio.run(test_maps_priority())
