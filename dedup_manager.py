# =============================================================
#  Job Hunter - Dedup Manager (Duplicate Prevention)
# =============================================================
import json, hashlib, os
from datetime import datetime

SEEN_FILE = os.path.join(os.path.dirname(__file__), "data", "seen_jobs.json")
LOG_FILE  = os.path.join(os.path.dirname(__file__), "data", "search_log.json")

def _load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_seen(data):
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def make_id(job: dict) -> str:
    key = (job.get("url") or job.get("link") or "") + (job.get("title") or "")
    return hashlib.md5(key.lower().strip().encode()).hexdigest()

def is_new(job: dict) -> bool:
    seen = _load_seen()
    return make_id(job) not in seen

def mark_seen(job: dict):
    seen = _load_seen()
    seen[make_id(job)] = {
        "title": job.get("title"),
        "url":   job.get("url") or job.get("link"),
        "seen_at": datetime.now().isoformat()
    }
    _save_seen(seen)

def clear_seen():
    _save_seen({})

def seen_count() -> int:
    return len(_load_seen())

# ---- Search Log ----
def log_search(source: str, keyword: str, found: int, sent: int, status: str, note: str = ""):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    logs.append({
        "time":    datetime.now().isoformat(),
        "source":  source,
        "keyword": keyword,
        "found":   found,
        "sent":    sent,
        "status":  status,
        "note":    note,
    })
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def get_logs(limit=200):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)
    return logs[-limit:]

def clear_logs():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
