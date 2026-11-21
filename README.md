<h1 align="center">HK Job Hunter</h1>

<p align="center"><b>Finds fresh IT and network job posts and notifies you on Telegram</b></p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/updated-2026--06--03-success" alt="Updated">
  <a href="https://github.com/alisadhk/hk-job-hunter/releases/latest"><img src="https://img.shields.io/badge/downloads-Releases-blue" alt="Releases"></a>
</p>

---

## Overview
A PyQt6 desktop tool that searches LinkedIn jobs and posts for Baghdad/Iraq (free, no API key), removes duplicates and sends new results to your Telegram chat.

## Features
- LinkedIn guest job search and LinkedIn posts search
- Duplicate filtering between runs
- Telegram notifications
- Editable keywords, locations and search interval
- Free to run: uses LinkedIn's public guest endpoints and web search, no paid API
- Remembers seen jobs so you only get new ones
- Test Telegram button to verify your bot settings

## How it works
- For every keyword and location the tool queries the LinkedIn guest job search and runs web searches for LinkedIn posts.
- Results are cleaned and de-duplicated against a local history file.
- New results appear in the table and are sent to your Telegram chat.
- With **Auto-run every** or **Continuous Monitoring Mode** it repeats on its own.

## Requirements
- Python 3.10+ with PyQt6 and requests.
- A Telegram bot token and chat ID for notifications (optional).

## Screenshots
<p align="center"><img src="screenshots/screenshot-1.png" alt="HK Job Hunter screenshot" width="720"></p>

## Download and install
### Option A - Ready-to-run download (recommended)
1. Open the **[Releases page](https://github.com/alisadhk/hk-job-hunter/releases/latest)**.
2. Download the file(s) listed under **Assets**:

| File | Size |
|---|---|
| `HK-Job-Hunter-source.zip` | 0 MB |

3. Run it. 

### Option B - Run from source
Requirements: Windows 10/11 and Python 3.10+.

```bash
git clone https://github.com/alisadhk/hk-job-hunter.git
cd hk-job-hunter
python -m pip install -r requirements.txt
python main.py
```

## How to use
1. Create a Telegram bot with **@BotFather** and note its token; get your chat ID.
2. Copy config.example.py to config.py and put your token and chat ID in it.
3. Install the requirements and run `python main.py`.
4. Adjust keywords and locations in the settings tab, then press Start.

## Configuration and privacy
- config.py and the data/ folder are ignored by git, so your token and history stay private.
- The example config contains only placeholders.
- The Arabic search words in the code are intentional (Iraqi job posts).

## Troubleshooting
- HTTP 429: LinkedIn rate-limited you; wait and increase the interval.
- No Telegram message: use **Test Telegram** and re-check the token/chat ID.
- Empty results: widen the keywords or the time range.

## Build the executable yourself
```bash
python -m pip install pyinstaller
python -m PyInstaller --noconfirm hk-job-hunter.spec
```
The executable is created in the `dist/` folder.

## Notes
- Respect the terms of the sites you search.

---

<p align="center">Maintained by <a href="https://github.com/alisadhk">@alisadhk</a> - last update 2026-06-03</p>