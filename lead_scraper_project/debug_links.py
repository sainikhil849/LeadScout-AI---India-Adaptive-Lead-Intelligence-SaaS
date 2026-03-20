from bs4 import BeautifulSoup

def analyze(filename, label):
    print(f"\n--- {label} ---")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        print(f"Total links: {len(links)}")
        
        # Look for profile-like links
        print("Profile-like links (first 30):")
        count = 0
        for l in links:
            l_l = l.lower()
            # JD patterns
            is_jd = ('-nct-' in l_l or '-dc-' in l_l or 'nct-' in l_l or 'dc-' in l_l) and '/hyderabad/' in l_l
            # Sulekha patterns
            is_sk = 'sulekha.com/' in l_l and len(l_l) > 40
            
            if is_jd or is_sk:
                print(l)
                count += 1
            if count >= 30:
                break
    except Exception as e:
        print(f"Error {label}: {e}")

analyze('jd.html', 'JustDial')
analyze('sk.html', 'Sulekha')
