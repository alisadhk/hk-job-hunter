# hk-job-hunter 🔍

Automated job search tool for Baghdad/Iraq on LinkedIn with Telegram notifications.

## Project Structure

```
hk-job-hunter/
├── main.py              ← GUI (PyQt6)
├── config.py            ← Settings + API keys
├── search_engine.py     ← Main search orchestrator
├── google_searcher.py   ← Google Custom Search + Dork builder
├── telegram_bot.py      ← Telegram notifications
├── dedup_manager.py     ← Duplicate prevention + logging
├── requirements.txt     ← Dependencies
└── data/
    ├── seen_jobs.json   ← Previously sent jobs
    ├── search_log.json  ← Search history log
    └── google_quota.json← Google API usage tracker
```

## Installation

```bash
# 1. Create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

## Configuration (config.py)

Set your API keys in `config.py`:

```python
TELEGRAM_TOKEN   = "your bot token"
TELEGRAM_CHAT_ID = "your chat id"
GOOGLE_API_KEY   = "Google Custom Search key"
GOOGLE_CX        = "Search Engine ID"
JSEARCH_API_KEY  = "RapidAPI key (optional)"
```

### Google Custom Search Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **Custom Search API**
3. Create an API key and a Custom Search Engine ID

### JSearch API Setup (Optional)
1. Create a free account on [RapidAPI](https://rapidapi.com/)
2. Subscribe to [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
3. Copy your RapidAPI key into `JSEARCH_API_KEY`

## Usage

1. Run `python main.py`
2. Add/edit keywords
3. Choose the time range (day / week / month / auto)
4. Click ▶ Start Search
5. New results are automatically sent to Telegram

## API Notes

- Google Custom Search: 100 free searches per day
- JSearch API: 500 free requests per month
- The app tracks usage automatically and displays it in the log
- When quota runs out, that source is skipped and logged
