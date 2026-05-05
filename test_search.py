import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re

def test_yahoo():
    keyword = "Network Engineer"
    dork = 'site:linkedin.com/posts "Network Engineer" ("Baghdad" OR "Iraq" OR "بغداد" OR "العراق" OR "Baghdad Iraq") ("hiring" OR "vacancy" OR "looking for" OR "join our team" OR "recruiting" OR "open position" OR "send your cv" OR "send your resume")'
    url = "https://search.yahoo.com/search?p=" + urllib.parse.quote_plus(dork)
    print("URL:", url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    req = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(req).read()
    open('yahoo_test.html','wb').write(html)
    
    soup = BeautifulSoup(html, 'html.parser')
    blocks = soup.find_all('div', class_=re.compile(r'algo-sr|algo(?!\w)'))
    print(f"Blocks found: {len(blocks)}")
    
    for b in blocks:
        a_tag = b.find("a", href=True)
        link = a_tag['href'] if a_tag else ""
        if 'r.search.yahoo.com/_ylt=' in link:
            match = re.search(r'RU=([^/]+)/RK=', link)
            if match:
                link = urllib.parse.unquote(match.group(1))
        
        title = b.find("h3")
        title_text = title.text if title else "No Title"
        print(f"Title: {title_text}")
        print(f"Link: {link}")
test_yahoo()
