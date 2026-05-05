# =============================================================
#  Job Hunter - Web Posts Searcher (Yahoo/Bing Engine)
# =============================================================
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
from config import LOCATION_VARIANTS

# --- القواميس المركزية للبحث عن الوظائف ---
INTENT_KEYWORDS = [
    # English
    "hiring", "vacancy", "looking for", "join our team", "recruiting",
    "open position", "send your cv", "send your resume", "opportunity",
    "required", "now hiring", "job opening",
    # Arabic
    "مطلوب", "فرصة عمل", "وظيفة", "تعيين", "للتعيين", "نبحث عن",
    "شاغر", "شواغر", "انضم لفريقنا", "ارسال السيرة", "للعمل",
    "بحاجة الى", "تعلن شركة"
]

def chunk_list(lst, max_words=10):
    for i in range(0, len(lst), max_words):
        yield lst[i:i + max_words]

def search_google_posts(keyword: str, log_cb=None) -> list:
    """Use free Yahoo Search scraping to find LinkedIn posts smoothly!"""
    results = []
    seen_urls = set()
    found_count = 0

    # 1. Location part: we take max 5 variations to keep the query reasonably sized
    locs = [f'"{loc}"' for loc in LOCATION_VARIANTS[:5]]
    loc_part = "(" + " OR ".join(locs) + ")"

    # 2. Chop Intent into batches of 8 max
    intent_chunks = list(chunk_list(INTENT_KEYWORDS, max_words=8))

    if log_cb:
        log_cb("google", f"🔄 Web Posts Engine: '{keyword}' split into {len(intent_chunks)} Yahoo deep search chunks.", "info")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    for i, chunk in enumerate(intent_chunks):
        intent_part = "(" + " OR ".join([f'"{c}"' for c in chunk]) + ")"
        
        # Build the exact dork
        dork = f'site:linkedin.com/posts "{keyword}" {loc_part} {intent_part}'

        try:
            # Short sleep is enough for Yahoo, completely bypasses 429 Google rate limits
            if i > 0:
                time.sleep(3)

            url = "https://search.yahoo.com/search?p=" + urllib.parse.quote_plus(dork)
            req = urllib.request.Request(url, headers=headers)
            
            # Fetch HTML without proxy, without headless browsers!
            html = urllib.request.urlopen(req, timeout=12).read()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Yahoo wraps results in div with class "algo-sr" or similar "algo"
            search_blocks = soup.find_all('div', class_=re.compile(r'algo-sr|algo(?!\w)'))
            
            chunk_results_count = 0
            for block in search_blocks:
                a_tag = block.find('a', href=True)
                if not a_tag:
                    continue
                
                title_elem = block.find('h3', class_=re.compile(r'title|d-ib|mt-0'))
                if not title_elem:
                    title_elem = block.find('h3')
                    if not title_elem:
                        continue
                
                link = a_tag['href']
                
                # Yahoo wraps links in redirects sometimes
                if 'r.search.yahoo.com/_ylt=' in link:
                    # Clean out RU tracking
                    match = re.search(r'RU=([^/]+)/RK=', link)
                    if match:
                        link = urllib.parse.unquote(match.group(1))
                
                # Strictly filter non-posts (just in case)
                if "linkedin.com/posts" not in link:
                    continue
                    
                if link in seen_urls:
                    continue
                
                seen_urls.add(link)
                
                desc_elem = block.find('div', class_=re.compile(r'compText'))
                snippet = desc_elem.text.strip() if desc_elem else ""

                results.append({
                    "title":   title_elem.text.strip().replace(" | LinkedIn", ""),
                    "url":     link,
                    "snippet": snippet,
                    "source":  f"LinkedIn Post",
                    "keyword": keyword,
                    "company": "",
                    "location": "Baghdad/Iraq"
                })
                found_count += 1
                chunk_results_count += 1

            if log_cb:
                log_cb("google", f"   ↳ Chunk {i+1} found {chunk_results_count} posts.", "info")

        except Exception as e:
            if log_cb:
                log_cb("google", f"⛔ Post search error in chunk {i+1}: {str(e)}", "error")
            break  # Break out if network error occurs

    if log_cb:
        log_cb("linkedin", f"✅ Web Posts ('{keyword}'): Finished checking all chunks -> Total unique found: {found_count}", "success")
    
    return results

def build_dork(keyword: str, date_range: str = "week") -> str:
    locs = [f'"{loc}"' for loc in LOCATION_VARIANTS[:4]]
    loc_part = "(" + " OR ".join(locs) + ")"
    return f'site:linkedin.com/posts "{keyword}" {loc_part}'

def build_all_dorks(keywords: list, date_range: str = "week") -> list:
    return [{"keyword": kw, "query": build_dork(kw, date_range)} for kw in keywords]
