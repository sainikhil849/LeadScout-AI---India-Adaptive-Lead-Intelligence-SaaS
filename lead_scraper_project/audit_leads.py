import pandas as pd
import os

def audit():
    file_path = r"c:\Users\saini\OneDrive\Desktop\codes\cycleauto\lead_scraper_project\leads_Yoga_Hyderabad.xlsx"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    df = pd.read_excel(file_path)
    print(f"Total leads: {len(df)}")
    print("\nColumns found:", list(df.columns))
    
    # Check for empty fields
    print("\nField Fill Rates:")
    for col in df.columns:
        filled = df[col].notna().sum()
        print(f" - {col}: {filled}/{len(df)} ({(filled/len(df))*100:.1f}%)")

    print("\nSample Data (Top 5):")
    print(df[['name', 'phone', 'address', 'rating']].head(5).to_string())

if __name__ == "__main__":
    audit()
