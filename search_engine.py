# =============================================================
#  Job Hunter - Search Orchestrator
# =============================================================
import requests, time
from google_searcher    import search_google_posts
from dedup_manager      import is_new, mark_seen, log_search
from telegram_bot       import send_job, send_summary, send_error
from config             import LOCATION_VARIANTS
from linkedin_scraper   import search_linkedin_direct




def _process_results(results, source_name, log_cb, result_cb, stop_flag, counters):
    """Helper to process results: strict location filter, deduplicate, send to Telegram, log."""
    def _log(src, msg, lvl="info"):
        if log_cb:
            log_cb(src, msg, lvl)

    for job in results:
        if stop_flag and stop_flag():
            _log("system", "🛑 Search stopped by user request", "warning")
            break

        # STRICT LOCATION FILTER
        # User explicitly requested ONLY Baghdad/Iraq jobs.
        loc_str = (job.get("location", "") + " " + job.get("title", "") + " " + job.get("snippet", "")).lower()
        iraq_words = ["iraq", "baghdad", "عراق", "بغداد", "erbil", "اربيل", "basra", "بصرة", "najaf", "نجف", "mosul", "موصل", "[iq]"]
        if not any(word in loc_str for word in iraq_words):
            _log("system", f"🚫 Dropped (Not Iraq): {job.get('title','')[:40]} [{job.get('location','')}]", "warning")
            continue

        if is_new(job):
            mark_seen(job)
            ok = send_job(job)
            if ok:
                counters["sent"] += 1
                _log("telegram", f"📤 Sent: {job.get('title','')[:60]}", "success")
            else:
                _log("telegram", f"⛔ Failed to send: {job.get('title','')[:60]}", "error")
            if result_cb:
                result_cb(job)
        else:
            _log("system", f"🔁 Duplicate, skipped: {job.get('title','')[:60]}", "info")

        log_search(source_name, job.get("keyword", ""), 1,
                   1 if is_new(job) else 0, "ok")


def run_search(keywords: list, date_range: str = "week",
               log_cb=None, result_cb=None, stop_flag=None):
    """
    Main search orchestrator.
    Searches 2 sources: LinkedIn Direct (Jobs) and LinkedIn Posts.
    """
    counters = {"found": 0, "sent": 0}

    def _log(src, msg, lvl="info"):
        if log_cb:
            log_cb(src, msg, lvl)

    _log("system", f"🚀 Search started | Date range: {date_range} | Keywords: {len(keywords)}", "success")

    # ======== SOURCE 1: LinkedIn Direct Scraper (FREE, best source) ========
    _log("linkedin", "🔍 Searching LinkedIn directly (Free / No Key)...", "info")
    for i, kw in enumerate(keywords):
        if stop_flag and stop_flag():
            _log("system", "🛑 Search stopped by user request", "warning")
            break

        li_results = search_linkedin_direct(kw, location="Iraq", log_cb=_log)
        counters["found"] += len(li_results)
        _process_results(li_results, "LinkedIn", _log, result_cb, stop_flag, counters)

        if i < len(keywords) - 1:
            time.sleep(2)

    # ======== SOURCE 2: LinkedIn Posts (Free Web Search) ========
    _log("linkedin", f"🔍 Searching LinkedIn POSTS (via Free Search)...", "info")
    for i, kw in enumerate(keywords):
        if stop_flag and stop_flag():
            _log("system", "🛑 Search stopped by user request", "warning")
            break

        post_results = search_google_posts(kw, log_cb=_log)
        counters["found"] += len(post_results)
        _process_results(post_results, "LinkedIn Posts", _log, result_cb, stop_flag, counters)

        if i < len(keywords) - 1:
            time.sleep(2)

    # ======== Summary ========
    sources = "LinkedIn Jobs + LinkedIn Posts"

    _log("system",
         f"✅ Search complete | Total: {counters['found']} | New: {counters['sent']} | "
         f"Duplicates: {counters['found']-counters['sent']}",
         "success")
    send_summary(counters["found"], counters["sent"], keywords, sources)

    return {"found": counters["found"], "sent": counters["sent"]}
