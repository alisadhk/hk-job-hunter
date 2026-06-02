import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from config import GOOGLE_API_KEY, GOOGLE_CX

def check_api():
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx":  GOOGLE_CX,
        "q":   "test",
        "num": 1
    }
    
    print(f"Checking API Key: {GOOGLE_API_KEY[:10]}...")
    print(f"Checking CX: {GOOGLE_CX}")
    
    try:
        resp = requests.get(url, params=params)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print("Response body:")
            print(resp.text)
        else:
            print("API OK! Results received.")
            data = resp.json()
            items = data.get("items", [])
            print(f"Found {len(items)} results")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()
