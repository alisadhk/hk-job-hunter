import requests
from bs4 import BeautifulSoup
import re

def search_ddg_posts(keyword):
    query = f'site:linkedin.com/posts "{keyword}" ("Baghdad" OR "Iraq" OR "بغداد" OR "العراق") ("hiring" OR "وظيفة")'
    print(f"Query: {query}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    url = f"https://html.duckduckgo.com/html/?q={query}"
    
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = soup.find_all('a', class_='result__url')
            
            for a in results:
                print(a.get('href'))
        else:
            print(f"Failed with status: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")

search_ddg_posts("Network")
