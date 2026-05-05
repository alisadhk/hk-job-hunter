# =============================================================
#  hk-job-hunter - Telegram Notifier
# =============================================================
import requests
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_message(text: str, parse_mode: str = "HTML") -> bool:
    try:
        resp = requests.post(
            f"{BASE_URL}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text,
                  "parse_mode": parse_mode, "disable_web_page_preview": False},
            timeout=15
        )
        return resp.status_code == 200
    except Exception:
        return False

def send_job(job: dict) -> bool:
    title   = job.get("title", "No Title")
    company = job.get("company", "")
    loc     = job.get("location", "")
    snippet = job.get("snippet", "")
    url     = job.get("url") or job.get("link", "")
    source  = job.get("source", "")
    keyword = job.get("keyword", "")
    dork    = job.get("dork", "")
    now     = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = ["🔔 <b>New Job Found!</b>", ""]
    lines.append(f"📌 <b>Title:</b> {title}")
    if company:
        lines.append(f"🏢 <b>Company:</b> {company}")
    if loc:
        lines.append(f"📍 <b>Location:</b> {loc}")
    if snippet:
        lines.append(f"📝 <b>Details:</b> {snippet[:300]}{'...' if len(snippet)>300 else ''}")
    lines.append(f"🔍 <b>Keyword:</b> {keyword}")
    lines.append(f"⚙️ <b>Source:</b> {source}")
    lines.append(f"🕐 <b>Found at:</b> {now}")
    if url:
        lines.append(f"\n🔗 <a href='{url}'>Open Link</a>")
    if dork:
        lines.append(f"\n<code>🔎 {dork[:200]}</code>")

    return send_message("\n".join(lines))

def send_summary(total_found: int, total_sent: int, keywords: list, source: str):
    now  = datetime.now().strftime("%Y-%m-%d %H:%M")
    text = (
        f"📊 <b>Search Report</b>\n\n"
        f"🕐 Time: {now}\n"
        f"⚙️ Source: {source}\n"
        f"🔍 Keywords: {len(keywords)}\n"
        f"📥 Total results: {total_found}\n"
        f"📤 New jobs sent: {total_sent}\n"
        f"🔁 Duplicates (skipped): {total_found - total_sent}"
    )
    send_message(text)

def send_error(msg: str):
    send_message(f"⛔ <b>hk-job-hunter Error:</b>\n{msg}")

def test_connection() -> bool:
    try:
        resp = requests.get(f"{BASE_URL}/getMe", timeout=10)
        return resp.status_code == 200
    except Exception:
        return False
