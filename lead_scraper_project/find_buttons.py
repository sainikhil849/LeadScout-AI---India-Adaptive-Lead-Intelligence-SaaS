from bs4 import BeautifulSoup
import re

def analyze_buttons(file_path):
    print(f"\n--- Analyzing {file_path} ---")
    soup = BeautifulSoup(open(file_path, encoding='utf-8').read(), 'html.parser')
    
    # Track common patterns for contact reveal
    keywords = ["Number", "Call", "Contact", "Show", "View"]
    
    found = 0
    for el in soup.find_all(['span', 'button', 'a', 'div']):
        text = el.get_text(strip=True)
        if text and any(k in text for k in keywords) and len(text) < 30:
            classes = el.get('class', [])
            tag = el.name
            attrs = {k: v for k, v in el.attrs.items() if k != 'class'}
            print(f"[{tag}] '{text}' | class={classes} | other={attrs}")
            found += 1
            if found > 40: break

if __name__ == "__main__":
    analyze_buttons('jd.html')
    analyze_buttons('sk.html')
