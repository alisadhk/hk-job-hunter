# =============================================================
#  Job Hunter - LinkedIn Direct Scraper (Free / No Key)
#  Uses LinkedIn's public guest job search API (no auth needed)
# =============================================================
import requests, re, time

def search_linkedin_direct(keyword: str, location: str = "Iraq", log_cb=None) -> list:
    """
    Scrape LinkedIn's public job search page (guest API).
    No API key, no login required.
    """
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        "keywords": keyword,
        "location": location,
        "start": 0,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    def _log(src, msg, lvl="info"):
        if log_cb:
            log_cb(src, msg, lvl)

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)

        if resp.status_code == 429:
            _log("linkedin", "⛔ LinkedIn: Rate limited (429) — Try again later", "error")
            return []

        if resp.status_code != 200:
            _log("linkedin", f"⛔ LinkedIn scraper error: {resp.status_code}", "error")
            return []

        html = resp.text
        if len(html) < 100:
            _log("linkedin", f"ℹ️ LinkedIn: No jobs found for '{keyword}' in {location}", "info")
            return []

        # Parse results using regex (no external dependency needed)
        results = []

        # Extract titles
        titles = re.findall(r'base-search-card__title[^>]*>([^<]+)<', html)
        # Extract companies (may be inside nested <a> tags)
        companies = re.findall(r'base-search-card__subtitle[^>]*>\s*(?:<[^>]*>)?\s*([^<]+)', html)
        # Extract locations
        locations = re.findall(r'job-search-card__location[^>]*>([^<]+)<', html)
        # Extract links
        links = re.findall(r'href="(https://[^"]*linkedin\.com/jobs/view/[^"]*)"', html)

        count = min(len(titles), len(links))
        for i in range(count):
            results.append({
                "title":    titles[i].strip() if i < len(titles) else "",
                "company":  companies[i].strip() if i < len(companies) else "",
                "location": locations[i].strip() if i < len(locations) else "",
                "url":      links[i].split("?")[0] if i < len(links) else "",
                "snippet":  "",
                "source":   "LinkedIn (Direct Scrape)",
                "keyword":  keyword,
            })

        _log("linkedin", f"✅ LinkedIn Direct: '{keyword}' → {len(results)} jobs", "success")
        return results

    except requests.exceptions.Timeout:
        _log("linkedin", f"⏱️ LinkedIn scraper timeout for: {keyword}", "warning")
        return []
    except Exception as e:
        _log("linkedin", f"⛔ LinkedIn scraper error: {str(e)}", "error")
        return []


def search_all_keywords_linkedin(keywords: list, location: str = "Iraq", log_cb=None) -> list:
    """Search all keywords on LinkedIn's public guest API."""
    all_results = []
    for i, kw in enumerate(keywords):
        results = search_linkedin_direct(kw, location, log_cb)
        all_results.extend(results)

        # Delay between requests to avoid rate limiting
        if i < len(keywords) - 1:
            time.sleep(2)

    return all_results


