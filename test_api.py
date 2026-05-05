import requests

API_KEY = "AIzaSyDrhY2ZusdCmPGyk_38z5ypIXFsCNh8DIg"
CX = "e763eed2e84bf4f87"

url = "https://www.googleapis.com/customsearch/v1"
params = {
    "key": API_KEY,
    "cx": CX,
    "q": "site:linkedin.com/posts hiring",
    "num": 2,
}

print("Testing Google Custom Search API...")
response = requests.get(url, params=params)
print(f"Status Code: {response.status_code}")
print(response.json())
