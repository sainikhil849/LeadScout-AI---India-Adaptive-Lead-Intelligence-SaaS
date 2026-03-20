from bs4 import BeautifulSoup
import re

jd_html = open('jd.html', encoding='utf-8').read()
sk_html = open('sk.html', encoding='utf-8').read()

jd_soup = BeautifulSoup(jd_html, 'html.parser')
sk_soup = BeautifulSoup(sk_html, 'html.parser')

print("JD Total Links:", len(jd_soup.find_all('a')))
print("\nJD Links that look like profiles:")
jd_count = 0
for a in jd_soup.find_all('a', href=True):
    href = a['href']
    if 'Hyderabad/' in href and '-' in href and not 'javascript' in href and jd_count < 10:
        print(a.get('class', []), href[:100])
        jd_count += 1

print("\nSK Total Links:", len(sk_soup.find_all('a')))
print("SK Links that look like profiles:")
sk_count = 0
for a in sk_soup.find_all('a', href=True):
    href = a['href']
    if len(href) > 20 and not href.startswith('javascript') and sk_count < 10:
        if 'dance' in href.lower() and 'contact' not in href.lower():
            print(a.get('class', []), href[:100])
            sk_count += 1
