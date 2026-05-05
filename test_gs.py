import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from googlesearch import search

def test_gs(keyword):
    query = f'site:linkedin.com/posts "{keyword}" ("Baghdad" OR "Iraq" OR "بغداد" OR "العراق")'
    print(f"Query: {query}")
    try:
        # returns an iterator of results, advanced=True returns objects
        results = search(query, advanced=True, num_results=10)
        found = 0
        for r in results:
            found += 1
            print(f"- {r.title}")
            print(f"  {r.url}")
        print(f"Total found: {found}\n")
    except Exception as e:
        print(f"Error: {e}")

test_gs("Network")
test_gs("وظيفة")
