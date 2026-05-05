# =============================================================
#  Job Hunter - Main GUI (PyQt6)
# =============================================================
import sys, json, os, threading
from datetime import datetime

# Add the current directory to sys.path to ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QGroupBox,
    QRadioButton, QButtonGroup, QSpinBox, QScrollArea,
    QFrame, QSizePolicy, QMessageBox, QProgressBar, QToolButton,
    QDialog, QFormLayout
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QObject
)
from PyQt6.QtGui import (
    QFont, QColor, QTextCursor
)

import config
from dedup_manager  import clear_seen, clear_logs, get_logs, seen_count
from google_searcher import build_all_dorks
from telegram_bot   import test_connection, send_message
from search_engine  import run_search

# ──────────────────────────────────────────────
#  THEME
# ──────────────────────────────────────────────
DARK = {
    "bg":        "#0d1117",
    "bg2":       "#161b22",
    "bg3":       "#21262d",
    "border":    "#30363d",
    "accent":    "#58a6ff",
    "accent2":   "#1f6feb",
    "green":     "#3fb950",
    "yellow":    "#d29922",
    "red":       "#f85149",
    "text":      "#e6edf3",
    "text2":     "#8b949e",
    "text3":     "#484f58",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {DARK['bg']};
    color: {DARK['text']};
    font-family: 'Segoe UI', 'Consolas', monospace;
    font-size: 13px;
}}
QGroupBox {{
    border: 1px solid {DARK['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding: 8px;
    font-weight: bold;
    color: {DARK['accent']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
}}
QPushButton {{
    background-color: {DARK['bg3']};
    border: 1px solid {DARK['border']};
    border-radius: 6px;
    padding: 8px 18px;
    color: {DARK['text']};
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {DARK['accent2']};
    border-color: {DARK['accent']};
    color: #ffffff;
}}
QPushButton:pressed {{
    background-color: {DARK['accent']};
}}
QPushButton#btn_start {{
    background-color: #1a4a1a;
    border-color: {DARK['green']};
    color: {DARK['green']};
    font-size: 14px;
    padding: 10px 24px;
}}
QPushButton#btn_start:hover {{
    background-color: {DARK['green']};
    color: #000;
}}
QPushButton#btn_stop {{
    background-color: #4a1a1a;
    border-color: {DARK['red']};
    color: {DARK['red']};
    font-size: 14px;
    padding: 10px 24px;
}}
QPushButton#btn_stop:hover {{
    background-color: {DARK['red']};
    color: #fff;
}}
QPushButton#btn_clear {{
    background-color: #3a2a0a;
    border-color: {DARK['yellow']};
    color: {DARK['yellow']};
}}
QPushButton#btn_clear:hover {{
    background-color: {DARK['yellow']};
    color: #000;
}}
QLineEdit, QTextEdit, QSpinBox {{
    background-color: {DARK['bg2']};
    border: 1px solid {DARK['border']};
    border-radius: 6px;
    padding: 6px 10px;
    color: {DARK['text']};
    selection-background-color: {DARK['accent2']};
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
    border-color: {DARK['accent']};
}}
QTableWidget {{
    background-color: {DARK['bg2']};
    border: 1px solid {DARK['border']};
    border-radius: 6px;
    gridline-color: {DARK['border']};
    color: {DARK['text']};
    alternate-background-color: {DARK['bg3']};
}}
QTableWidget::item {{
    padding: 6px;
    border: none;
}}
QTableWidget::item:selected {{
    background-color: {DARK['accent2']};
    color: #fff;
}}
QHeaderView::section {{
    background-color: {DARK['bg3']};
    border: none;
    border-bottom: 2px solid {DARK['accent']};
    padding: 8px;
    font-weight: bold;
    color: {DARK['accent']};
}}
QRadioButton {{
    color: {DARK['text']};
    spacing: 8px;
}}
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid {DARK['border']};
    background: {DARK['bg3']};
}}
QRadioButton::indicator:checked {{
    background: {DARK['accent']};
    border-color: {DARK['accent']};
}}
QScrollBar:vertical {{
    background: {DARK['bg2']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {DARK['border']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {DARK['accent']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QSplitter::handle {{
    background: {DARK['border']};
    width: 2px;
}}
QProgressBar {{
    background: {DARK['bg3']};
    border: 1px solid {DARK['border']};
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background: {DARK['accent']};
    border-radius: 4px;
}}
QLabel#header_label {{
    font-size: 22px;
    font-weight: bold;
    color: {DARK['accent']};
    letter-spacing: 2px;
}}
QLabel#sub_label {{
    font-size: 11px;
    color: {DARK['text2']};
    letter-spacing: 1px;
}}
QFrame#separator {{
    background: {DARK['border']};
    max-height: 1px;
}}
"""

# ──────────────────────────────────────────────
#  Flow Layout (wraps widgets to next line)
# ──────────────────────────────────────────────
from PyQt6.QtWidgets import QLayout
from PyQt6.QtCore import QRect, QSize

class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._spacing = 4

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def setSpacing(self, spacing):
        self._spacing = spacing

    def spacing(self):
        return self._spacing

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        return size

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._doLayout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, test_only=False)

    def _doLayout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0

        for item in self._items:
            w = item.sizeHint().width()
            h = item.sizeHint().height()

            if x + w > rect.right() and line_height > 0:
                x = rect.x()
                y += line_height + self._spacing
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(x, y, w, h))

            x += w + self._spacing
            line_height = max(line_height, h)

        return y + line_height - rect.y()

# ──────────────────────────────────────────────
#  Worker Thread
# ──────────────────────────────────────────────
class SearchWorker(QObject):
    log_signal    = pyqtSignal(str, str, str)   # source, msg, level
    result_signal = pyqtSignal(dict)
    done_signal   = pyqtSignal(dict)

    def __init__(self, keywords, date_range):
        super().__init__()
        self.keywords   = keywords
        self.date_range = date_range
        self._stop      = False

    def stop(self):
        self._stop = True

    def run(self):
        result = run_search(
            keywords   = self.keywords,
            date_range = self.date_range,
            log_cb     = lambda s, m, l: self.log_signal.emit(s, m, l),
            result_cb  = lambda j: self.result_signal.emit(j),
            stop_flag  = lambda: self._stop,
        )
        self.done_signal.emit(result)

# ──────────────────────────────────────────────
#  Keyword Tag Widget
# ──────────────────────────────────────────────
class KeywordTag(QFrame):
    removed = pyqtSignal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.setStyleSheet(f"""
            QFrame {{
                background: {DARK['bg3']};
                border: 1px solid {DARK['accent2']};
                border-radius: 12px;
                padding: 1px 3px;
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 2, 3, 2)
        lay.setSpacing(3)

        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {DARK['accent']}; font-size: 10px; border: none; background: transparent;")
        lay.addWidget(lbl)

        btn = QToolButton()
        btn.setText("✕")
        btn.setFixedSize(16, 16)
        btn.setStyleSheet(f"""
            QToolButton {{
                color: {DARK['text3']};
                border: none;
                background: transparent;
                font-size: 10px;
                padding: 0;
            }}
            QToolButton:hover {{ color: {DARK['red']}; }}
        """)
        btn.clicked.connect(lambda: self.removed.emit(self.text))
        lay.addWidget(btn)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

# ──────────────────────────────────────────────
#  Keywords Panel
# ──────────────────────────────────────────────
class KeywordsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("🔑 Keywords", parent)
        self._keywords = list(config.DEFAULT_KEYWORDS)
        self._tags     = {}
        self._build()

    def _build(self):
        main = QVBoxLayout(self)
        main.setSpacing(8)

        # input row
        row = QHBoxLayout()
        self.inp = QLineEdit()
        self.inp.setPlaceholderText("Add keyword (separate multiple with space, comma, or dash)...")
        self.inp.returnPressed.connect(self._add_from_input)
        row.addWidget(self.inp)

        btn = QPushButton("+ Add")
        btn.setFixedWidth(80)
        btn.clicked.connect(self._add_from_input)
        row.addWidget(btn)
        main.addLayout(row)

        # tags area — use a wrapping flow layout
        self.tags_widget = QWidget()
        self.tags_flow = FlowLayout(self.tags_widget)
        self.tags_flow.setSpacing(4)

        scroll = QScrollArea()
        scroll.setWidget(self.tags_widget)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(100)
        scroll.setMaximumHeight(200)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea {{ border: 1px solid {DARK['border']}; border-radius: 6px; background: {DARK['bg2']}; }}")
        main.addWidget(scroll)

        for kw in self._keywords:
            self._add_tag(kw)

    def _parse_input(self, text: str) -> list:
        import re
        parts = re.split(r'[,،\-/|]+|\s{2,}', text)
        return [p.strip() for p in parts if p.strip()]

    def _add_from_input(self):
        raw = self.inp.text().strip()
        if not raw:
            return
        for kw in self._parse_input(raw):
            if kw and kw not in self._keywords:
                self._keywords.append(kw)
                self._add_tag(kw)
        self.inp.clear()
        self._save()

    def _add_tag(self, kw):
        tag = KeywordTag(kw)
        tag.removed.connect(self._remove)
        self.tags_flow.addWidget(tag)
        self._tags[kw] = tag

    def _remove(self, kw):
        if kw in self._keywords:
            self._keywords.remove(kw)
        if kw in self._tags:
            self._tags[kw].deleteLater()
            del self._tags[kw]
        self._save()

    def _save(self):
        config.DEFAULT_KEYWORDS = self._keywords[:]
        self.save_to_file()

    def save_to_file(self):
        """Persist keywords to config.py file."""
        import re
        config_path = os.path.join(os.path.dirname(__file__), "config.py")
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Replace DEFAULT_KEYWORDS list
        kw_str = ",\n".join([f'    "{kw}"' for kw in self._keywords])
        new_list = f"DEFAULT_KEYWORDS = [\n{kw_str},\n]"
        content = re.sub(
            r'DEFAULT_KEYWORDS\s*=\s*\[.*?\]',
            new_list,
            content,
            flags=re.DOTALL
        )
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    def get_keywords(self):
        return self._keywords[:]

# ──────────────────────────────────────────────
#  Log Panel
# ──────────────────────────────────────────────
class LogPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("📜 Activity Log", parent)
        lay = QVBoxLayout(self)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFont(QFont("Consolas", 11))
        self.log_box.setStyleSheet(f"""
            QTextEdit {{
                background: {DARK['bg']};
                border: 1px solid {DARK['border']};
                border-radius: 6px;
                color: {DARK['text']};
            }}
        """)
        lay.addWidget(self.log_box)

        btn_clear = QPushButton("🗑 Clear Log")
        btn_clear.setObjectName("btn_clear")
        btn_clear.setFixedWidth(130)
        btn_clear.clicked.connect(self.clear)
        lay.addWidget(btn_clear, alignment=Qt.AlignmentFlag.AlignRight)

    def append(self, source: str, msg: str, level: str = "info"):
        colors = {
            "success": DARK['green'],
            "warning": DARK['yellow'],
            "error":   DARK['red'],
            "info":    DARK['text2'],
        }
        src_colors = {
            "google":   "#f78166",
            "jsearch":  "#e3b341",
            "telegram": "#58a6ff",
            "system":   "#d2a8ff",
            "linkedin": "#0a66c2",
        }
        ts  = datetime.now().strftime("%H:%M:%S")
        col = colors.get(level, DARK['text2'])
        sc  = src_colors.get(source, DARK['text2'])

        html = (
            f'<span style="color:{DARK["text3"]}">[{ts}]</span> '
            f'<span style="color:{sc};font-weight:bold">[{source.upper()}]</span> '
            f'<span style="color:{col}">{msg}</span><br>'
        )
        self.log_box.moveCursor(QTextCursor.MoveOperation.End)
        self.log_box.insertHtml(html)
        self.log_box.moveCursor(QTextCursor.MoveOperation.End)

    def clear(self):
        self.log_box.clear()
        clear_logs()

# ──────────────────────────────────────────────
#  Dorks Panel
# ──────────────────────────────────────────────
class DorksPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("🔎 Active Dork Queries", parent)
        lay = QVBoxLayout(self)
        self.box = QTextEdit()
        self.box.setReadOnly(True)
        self.box.setFont(QFont("Consolas", 10))
        self.box.setFixedHeight(120)
        self.box.setStyleSheet(f"""
            QTextEdit {{
                background: {DARK['bg']};
                border: 1px solid {DARK['border']};
                border-radius: 6px;
                color: #7ee787;
            }}
        """)
        lay.addWidget(self.box)

    def update_dorks(self, keywords: list, date_range: str):
        self.box.clear()
        dorks = build_all_dorks(keywords, date_range)
        for d in dorks:
            self.box.append(f'[{d["keyword"]}]\n{d["query"]}\n')

# ──────────────────────────────────────────────
#  Results Table
# ──────────────────────────────────────────────
class ResultsTable(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("📋 Results", parent)
        lay = QVBoxLayout(self)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Title", "Company", "Location", "Source", "Link"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        lay.addWidget(self.table)

        row2 = QHBoxLayout()
        self.count_lbl = QLabel("0 results")
        self.count_lbl.setStyleSheet(f"color:{DARK['text2']};")
        row2.addWidget(self.count_lbl)
        row2.addStretch()
        btn = QPushButton("🗑 Clear Results")
        btn.setObjectName("btn_clear")
        btn.clicked.connect(self.clear)
        row2.addWidget(btn)
        lay.addLayout(row2)

    def add_job(self, job: dict):
        r = self.table.rowCount()
        self.table.insertRow(r)
        url = job.get("url") or job.get("link", "")

        self.table.setItem(r, 0, QTableWidgetItem(job.get("title", "")[:80]))
        self.table.setItem(r, 1, QTableWidgetItem(job.get("company", "")))
        self.table.setItem(r, 2, QTableWidgetItem(job.get("location", "")))
        self.table.setItem(r, 3, QTableWidgetItem(job.get("source", "")))

        link_item = QTableWidgetItem("🔗 Open")
        link_item.setForeground(QColor(DARK['accent']))
        link_item.setData(Qt.ItemDataRole.UserRole, url)
        self.table.setItem(r, 4, link_item)

        self.table.scrollToBottom()
        self.count_lbl.setText(f"{self.table.rowCount()} results")

    def clear(self):
        self.table.setRowCount(0)
        self.count_lbl.setText("0 results")
        clear_seen()

# ──────────────────────────────────────────────
#  Status Bar
# ──────────────────────────────────────────────
class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {DARK['bg2']};
                border-top: 1px solid {DARK['border']};
                padding: 4px 12px;
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 4, 8, 4)

        self.status_lbl  = QLabel("● Ready")
        self.quota_lbl   = QLabel("Google Quota: --/100")
        self.seen_lbl    = QLabel("Saved: 0")
        self.telegram_lbl = QLabel("Telegram: ●")

        for lbl in [self.status_lbl, self.quota_lbl, self.seen_lbl, self.telegram_lbl]:
            lbl.setStyleSheet(f"color:{DARK['text2']}; font-size:11px;")

        lay.addWidget(self.status_lbl)
        lay.addStretch()
        lay.addWidget(self.quota_lbl)
        lay.addWidget(self._sep())
        lay.addWidget(self.seen_lbl)
        lay.addWidget(self._sep())
        lay.addWidget(self.telegram_lbl)

    def _sep(self):
        f = QFrame()
        f.setFrameShape(QFrame.Shape.VLine)
        f.setStyleSheet(f"color:{DARK['border']};")
        return f

    def set_running(self, running: bool):
        if running:
            self.status_lbl.setText("● Searching...")
            self.status_lbl.setStyleSheet(f"color:{DARK['green']}; font-size:11px; font-weight:bold;")
        else:
            self.status_lbl.setText("● Ready")
            self.status_lbl.setStyleSheet(f"color:{DARK['text2']}; font-size:11px;")

    def refresh(self):
        self.quota_lbl.setText("Google Quota: Unlimited")
        self.seen_lbl.setText(f"Saved: {seen_count()}")

    def set_telegram(self, ok: bool):
        if ok:
            self.telegram_lbl.setText("Telegram: ●")
            self.telegram_lbl.setStyleSheet(f"color:{DARK['green']}; font-size:11px;")
        else:
            self.telegram_lbl.setText("Telegram: ✕")
            self.telegram_lbl.setStyleSheet(f"color:{DARK['red']}; font-size:11px;")

# ──────────────────────────────────────────────
#  Settings Dialog
# ──────────────────────────────────────────────
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Settings")
        self.setMinimumWidth(450)
        self.setStyleSheet(STYLESHEET)
        
        lay = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.tg_token = QLineEdit(config.TELEGRAM_TOKEN)
        self.tg_chat = QLineEdit(config.TELEGRAM_CHAT_ID)
        
        form.addRow("Telegram Token:", self.tg_token)
        form.addRow("Telegram Chat ID:", self.tg_chat)
        
        self.loc_variants = QLineEdit(", ".join(config.LOCATION_VARIANTS[:6]))
        self.loc_variants.setPlaceholderText("Iraq, Baghdad, Erbil ...")
        form.addRow("Location Keywords:", self.loc_variants)
        
        lay.addLayout(form)
        
        btn_lay = QHBoxLayout()
        self.btn_save = QPushButton("💾 Save Settings")
        self.btn_save.setStyleSheet(f"background-color: {DARK['green']}; color: #000;")
        self.btn_save.clicked.connect(self._save)
        
        self.btn_reset = QPushButton("🔄 Reset Defaults")
        self.btn_reset.clicked.connect(self._reset)
        
        btn_lay.addWidget(self.btn_reset)
        btn_lay.addWidget(self.btn_save)
        
        lay.addStretch()
        lay.addLayout(btn_lay)
        
    def _save(self):
        import re, os
        config_path = os.path.join(os.path.dirname(__file__), "config.py")
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = re.sub(r'TELEGRAM_TOKEN\s*=\s*".*?"', f'TELEGRAM_TOKEN  = "{self.tg_token.text().strip()}"', content)
        content = re.sub(r'TELEGRAM_CHAT_ID\s*=\s*".*?"', f'TELEGRAM_CHAT_ID = "{self.tg_chat.text().strip()}"', content)
        
        config.TELEGRAM_TOKEN = self.tg_token.text().strip()
        config.TELEGRAM_CHAT_ID = self.tg_chat.text().strip()
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        QMessageBox.information(self, "Success", "Settings saved successfully!")
        self.accept()

    def _reset(self):
        self.tg_token.setText("")
        self.tg_chat.setText("")
        self.loc_variants.setText("Baghdad, Iraq, بغداد, العراق")


# ──────────────────────────────────────────────
#  Main Window
# ──────────────────────────────────────────────
class MainWindow(QMainWindow):
    _log_signal = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔍 HK Job Hunter — Baghdad")
        self.setMinimumSize(1280, 820)
        self.resize(1440, 900)

        self._worker  = None
        self._thread  = None
        self._timer   = None
        self._running = False

        self._build_ui()
        self._check_telegram()
        self.status_bar.refresh()

        # auto-refresh status every 30s
        t = QTimer(self)
        t.timeout.connect(self.status_bar.refresh)
        t.start(30_000)

    # ── UI ──────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Main Splitter (Left side settings, Right side results)
        h_splitter = QSplitter(Qt.Orientation.Horizontal)
        h_splitter.setHandleWidth(4)

        # --- LEFT PANEL (Vertical: Controls, Schedule, Keywords) ---
        left_widget = QWidget()
        left_lay = QVBoxLayout(left_widget)
        left_lay.setContentsMargins(12, 12, 6, 6)
        left_lay.setSpacing(10)

        left_lay.addWidget(self._make_control_panel())
        left_lay.addWidget(self._make_schedule_panel())
        
        self.kw_panel = KeywordsPanel()
        left_lay.addWidget(self.kw_panel)
        left_lay.addStretch()

        h_splitter.addWidget(left_widget)

        # --- RIGHT PANEL (Vertical: Results, Logs) ---
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.setHandleWidth(4)

        self.results_table = ResultsTable()
        right_splitter.addWidget(self.results_table)

        self.log_panel = LogPanel()
        right_splitter.addWidget(self.log_panel)

        right_splitter.setSizes([900, 300])

        right_wrapper = QWidget()
        right_lay = QVBoxLayout(right_wrapper)
        right_lay.setContentsMargins(6, 12, 12, 6)
        right_lay.addWidget(right_splitter)

        h_splitter.addWidget(right_wrapper)
        h_splitter.setSizes([350, 1000])

        root.addWidget(h_splitter, stretch=1)

        # status bar
        self.status_bar = StatusBar()
        root.addWidget(self.status_bar)

    def _make_schedule_panel(self):
        grp = QGroupBox("⏱️ Search Time Range")
        lay = QVBoxLayout(grp)

        self._range_group = QButtonGroup(self)
        options = [
            ("Last 24 Hours", "day"),
            ("Last Week",     "week"),
            ("Last Month",    "month"),
        ]
        self._range_map = {}
        for label, val in options:
            rb = QRadioButton(label)
            if val == "week":
                rb.setChecked(True)
            self._range_group.addButton(rb)
            self._range_map[rb] = val
            rb.toggled.connect(self._update_dorks)
            lay.addWidget(rb)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{DARK['border']};")
        lay.addWidget(sep)

        auto_row = QHBoxLayout()
        self.auto_lbl = QLabel("Auto-run every:")
        auto_row.addWidget(self.auto_lbl)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 24)
        self.interval_spin.setValue(config.SEARCH_INTERVAL_HRS)
        self.interval_spin.setSuffix(" hrs")
        self.interval_spin.setFixedWidth(100)
        auto_row.addWidget(self.interval_spin)
        lay.addLayout(auto_row)

        self.auto_rb = QRadioButton("Continuous Monitoring Mode")
        self._range_group.addButton(self.auto_rb)
        self._range_map[self.auto_rb] = "auto"
        self.auto_rb.toggled.connect(self._update_dorks)
        lay.addWidget(self.auto_rb)

        return grp

    def _make_control_panel(self):
        grp = QGroupBox("🎛️ Controls")
        lay = QVBoxLayout(grp)

        self.btn_start = QPushButton("▶  Start Search")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.clicked.connect(self._start_search)

        self.btn_stop = QPushButton("⏹  Stop")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_search)

        self.btn_clear = QPushButton("🗑  Clear All")
        self.btn_clear.setObjectName("btn_clear")
        self.btn_clear.clicked.connect(self._clear_all)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)

        self.btn_settings = QPushButton("⚙️ Settings")
        self.btn_settings.setStyleSheet(f"background-color: {DARK['bg3']}; border: 1px solid {DARK['accent']}; color: {DARK['accent']};")
        self.btn_settings.clicked.connect(self._open_settings)

        self.btn_about = QPushButton("ℹ️ About")
        self.btn_about.clicked.connect(self._open_about)

        self.btn_help = QPushButton("❓ Help")
        self.btn_help.clicked.connect(self._open_help)

        self.btn_test_tg = QPushButton("🔔  Test Telegram")
        self.btn_test_tg.clicked.connect(self._test_telegram)

        row1 = QHBoxLayout()
        row1.addWidget(self.btn_start)
        row1.addWidget(self.btn_stop)

        lay.addLayout(row1)
        lay.addWidget(self.btn_clear)
        lay.addWidget(self.progress)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{DARK['border']};")
        lay.addWidget(sep)
        
        lay.addWidget(self.btn_settings)

        row_info = QHBoxLayout()
        row_info.addWidget(self.btn_about)
        row_info.addWidget(self.btn_help)
        lay.addLayout(row_info)
        
        lay.addWidget(self.btn_test_tg)

        lay.addStretch()

        return grp

    # ── Helpers ─────────────────────────────────
    def _get_date_range(self) -> str:
        for rb, val in self._range_map.items():
            if rb.isChecked():
                return val
        return "week"

    def _update_dorks(self):
        pass

    def _log(self, source: str, msg: str, level: str = "info"):
        self.log_panel.append(source, msg, level)

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
        
    def _open_about(self):
        QMessageBox.about(self, "About HK Job Hunter",
            "<h3>🔍 HK Job Hunter</h3>"
            "<p>Developed under the request and supervision of: <b>Ali</b></p>"
            "<p>A specialized automation tool designed to relentlessly monitor, collect, and display "
            "job vacancies across multiple online sources. It filters strict location metrics (like Iraq/Baghdad), "
            "removes daily duplicates, and forwards the best opportunities directly to your Telegram chat.</p>"
            "<p><i>Version 1.2</i></p>"
        )
        
    def _open_help(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Help & Instructions")
        msg.setText("<h3>📖 How to Use HK Job Hunter</h3>"
            "<p><b>General Idea:</b> This program autonomously scrapes LinkedIn (Jobs & Posts) to find fresh IT & Network job listings specifically localized to your targeted region (Iraq/Baghdad). It acts as a 24/7 background worker sending you VIP Telegram notifications.</p>"
            "<h4>🚀 Quick Start</h4>"
            "<ul>"
            "   <li><b>Keywords Panel:</b> Enter job titles like <code>Network Engineer</code>, <code>NOC</code>, or <code>IT Support</code>. Press Enter or click +Add.</li>"
            "   <li><b>Search Time Range:</b> Choose how far back to look for jobs. <i>Last 24 Hours</i> is recommended for daily checks.</li>"
            "   <li><b>Start Search:</b> Click the Play button to run a one-time scan. Found jobs populate the right table.</li>"
            "</ul>"
            "<h4>⚙️ Core Settings & Telegram Setup</h4>"
            "<ul>"
            "   <li>Open <b>Settings</b>. You MUST fill in the <code>Telegram Token</code> (from BotFather) and <code>Telegram Chat ID</code>.</li>"
            "   <li><b>Location Keywords:</b> This restricts the search. If a job doesn't mention 'Baghdad' or 'Iraq', it gets silently dropped to save your time.</li>"
            "   <li>Click <b>Test Telegram</b> down the controls panel to verify your bot is connected properly.</li>"
            "</ul>"
            "<h4>⏱️ Continuous Monitoring Mode</h4>"
            "<p>Select the <b>Continuous Monitoring Mode</b> radio button, choose the interval (e.g., every 3 hours), and click Start Search. The app will minimize its work to the background, running a cycle automatically every 3 hours and pushing new unique matches to your Telegram. Duplicates are never sent twice!</p>"
        )
        msg.exec()

    # ── Actions ─────────────────────────────────
    def _start_search(self):
        kws = self.kw_panel.get_keywords()
        if not kws:
            QMessageBox.warning(self, "Warning", "Add at least one keyword!")
            return

        dr = self._get_date_range()

        if dr == "auto":
            # Monitoring mode: run every X hours
            hrs = self.interval_spin.value()
            self._log("system", f"⏰ Monitoring mode: searching every {hrs} hour(s)", "info")
            self._do_single_search(kws, "day")
            self._timer = QTimer(self)
            self._timer.timeout.connect(lambda: self._do_single_search(kws, "day"))
            self._timer.start(hrs * 3600 * 1000)
        else:
            self._do_single_search(kws, dr)

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress.setVisible(True)
        self.status_bar.set_running(True)
        self._running = True

    def _do_single_search(self, kws, dr):
        self._worker = SearchWorker(kws, dr)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.log_signal.connect(self._log)
        self._worker.result_signal.connect(self.results_table.add_job)
        self._worker.done_signal.connect(self._on_done)
        self._thread.start()

    def _stop_search(self):
        if self._worker:
            self._worker.stop()
        if self._timer:
            self._timer.stop()
            self._timer = None
        self._log("system", "🛑 Stop requested...", "warning")
        self.btn_stop.setEnabled(False)

    def _on_done(self, result: dict):
        self._thread.quit()
        self.progress.setVisible(False)
        self.status_bar.refresh()
        self._log("system",
                  f"🏁 Search complete | Found: {result.get('found',0)} | Sent: {result.get('sent',0)}",
                  "success")

        if not self._timer:
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.status_bar.set_running(False)
            self._running = False

    def _clear_all(self):
        reply = QMessageBox.question(
            self, "Confirm", "This will clear all results, logs, and saved jobs memory. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.results_table.clear()
            self.log_panel.clear()
            clear_seen()
            clear_logs()
            self._log("system", "🗑 All data cleared (Including Duplicates Memory)", "warning")
            self.status_bar.refresh()

    def _check_telegram(self):
        def _check():
            ok = test_connection()
            self.status_bar.set_telegram(ok)
            level = "success" if ok else "error"
            msg   = "✅ Telegram connected successfully" if ok else "⛔ Telegram: Connection failed — Check your token"
            self._log("telegram", msg, level)
        threading.Thread(target=_check, daemon=True).start()

    def _test_telegram(self):
        def _send():
            ok = send_message("🔔 <b>HK Job Hunter</b>\nConnection test — Working successfully ✅")
            level = "success" if ok else "error"
            msg   = "✅ Test message sent to Telegram" if ok else "⛔ Failed to send test message"
            self._log("telegram", msg, level)
        threading.Thread(target=_send, daemon=True).start()

    def closeEvent(self, event):
        if self._worker:
            self._worker.stop()
        if self._timer:
            self._timer.stop()
        event.accept()


# ──────────────────────────────────────────────
#  Entry Point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
