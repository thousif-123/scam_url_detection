#!/usr/bin/env python3
"""
Corrected & cleaned version of user's `new_testing.py`.
Features:
 - URL normalization and consistent domain handling
 - Threaded analysis using a worker (no UI updates from worker thread)
 - Robust file I/O for whitelist / blacklist / dynamic blacklist
 - Loading spinner fallback
"""

import urllib.parse
import os
import re
import socket
import sys
import ipaddress

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtGui import QPixmap, QPainter, QMovie

# ---------- Worker class ----------
class AnalysisWorker(QObject):
    """
    Worker that runs a blocking function in a background thread.
    Emits 'finished' with the result dict, or 'error' with a message.
    """
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ---------------- Landing Page ---------------- #
class LandingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load background image (optional)
        bg_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "scam3.jpeg")
        self.bg = QPixmap(bg_path) if os.path.exists(bg_path) else QPixmap()

        # ---------------- Title ----------------
        title = QLabel("⚠️ SCAM URL DETECTOR ⚠️", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 48px; font-weight: bold; color: white;")

        # ---------------- Buttons ----------------
        btn_check = QPushButton("CHECK URL", self)
        btn_about = QPushButton("ABOUT US", self)
        btn_help = QPushButton("HELP", self)

        # Style buttons
        for btn in (btn_check, btn_about, btn_help):
            btn.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                background-color: #2E86C1;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
            """)
            btn.setFixedHeight(60)

        # Layouts
        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(10)
        top_row_layout.addWidget(btn_check)
        top_row_layout.addWidget(btn_about)
        top_row_layout.setAlignment(Qt.AlignHCenter)

        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.addWidget(btn_help)
        bottom_row_layout.setAlignment(Qt.AlignHCenter)

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addLayout(top_row_layout)
        layout.addLayout(bottom_row_layout)
        layout.addStretch(1)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(layout)

        # Navigation
        if parent:
            btn_check.clicked.connect(lambda: parent.display_page("analyzer"))
            btn_about.clicked.connect(lambda: parent.display_page("about"))
            btn_help.clicked.connect(lambda: parent.display_page("help"))

    def paintEvent(self, event):
        """Draw scaled background image (if available)."""
        painter = QPainter(self)
        if not self.bg.isNull():
            scaled = self.bg.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled)
        super().paintEvent(event)


# ---------------- Analyzer Page ---------------- #
class AnalyzerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        title = QLabel("🔎 URL Analyzer", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold;")

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter URL to check...")
        self.url_input.setFixedWidth(850)
        self.url_input.setFixedHeight(40)
        url_input_layout = QHBoxLayout()
        url_input_layout.addStretch()
        url_input_layout.addWidget(self.url_input)
        url_input_layout.addStretch()

        self.analyze_btn = QPushButton("Analyze", self)
        copy_btn = QPushButton("Copy Report", self)
        clear_btn = QPushButton("Clear", self)  # New Clear button

        btn_width = 180
        btn_height = 50
        for btn in (self.analyze_btn, copy_btn, clear_btn):
            btn.setFixedWidth(btn_width)
            btn.setFixedHeight(btn_height)
            btn.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                background-color: #2E86C1;
                color: white;
                border-radius: 8px;
            """)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.analyze_btn)
        buttons_layout.addWidget(copy_btn)
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addStretch()
        buttons_layout.setSpacing(15)

        risk_score_label = QLabel("Risk Score:", self)
        risk_score_label.setStyleSheet("font-size: 20px; font-weight: bold; color: red;")

        self.risk_score_box = QLabel("0%", self)
        self.risk_score_box.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: green;
            background-color: #f0f0f0;
            border: 2px solid #2E86C1;
            border-radius: 8px;
            padding: 5px 10px;
        """)
        self.risk_score_box.setFixedSize(120, 40)
        self.risk_score_box.setAlignment(Qt.AlignCenter)

        risk_score_container = QWidget()
        risk_score_container.setFixedWidth(850)
        risk_score_container_layout = QHBoxLayout(risk_score_container)
        risk_score_container_layout.addWidget(risk_score_label)
        risk_score_container_layout.addWidget(self.risk_score_box)
        risk_score_container_layout.addStretch()

        risk_score_main_layout = QHBoxLayout()
        risk_score_main_layout.addStretch()
        risk_score_main_layout.addWidget(risk_score_container)
        risk_score_main_layout.addStretch()

        self.result_status_label = QLabel("Result: --", self)
        self.result_status_label.setAlignment(Qt.AlignCenter)
        self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: black;")

        self.reasons_box = QTextEdit(self)
        self.reasons_box.setReadOnly(True)
        self.reasons_box.setPlaceholderText("Reasons will appear here...")
        self.reasons_box.setFixedSize(850, 200)

        reasons_box_layout = QHBoxLayout()
        reasons_box_layout.addStretch()
        reasons_box_layout.addWidget(self.reasons_box)
        reasons_box_layout.addStretch()

        home_btn = QPushButton("Home")
        about_btn = QPushButton("About Us")
        help_btn = QPushButton("Help")

        nav_buttons = [home_btn, about_btn, help_btn]
        nav_btn_width = 160
        nav_btn_height = 50
        for btn in nav_buttons:
            btn.setFixedWidth(nav_btn_width)
            btn.setFixedHeight(nav_btn_height)
            btn.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                background-color: #2E86C1;
                color: white;
                border-radius: 8px;
            """)

        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        nav_layout.addWidget(home_btn)
        nav_layout.addWidget(about_btn)
        nav_layout.addWidget(help_btn)
        nav_layout.addStretch()
        nav_layout.setSpacing(15)

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addLayout(url_input_layout)
        layout.addSpacing(10)
        layout.addLayout(buttons_layout)
        layout.addSpacing(20)
        layout.addLayout(risk_score_main_layout)
        layout.addSpacing(10)
        layout.addWidget(self.result_status_label, alignment=Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addLayout(reasons_box_layout)
        layout.addSpacing(20)
        layout.addLayout(nav_layout)
        layout.addStretch(1)

        self.setLayout(layout)
        # create loading spinner + fallback progress bar
        self._create_loading_widgets()

        # Files
        base_dir = os.path.abspath(os.path.dirname(__file__))
        self.blacklist_file = os.path.join(base_dir, "blacklist_urls.txt")
        self.whitelist_file = os.path.join(base_dir, "whitelist_urls.txt")
        self.dynamic_blacklist_file = os.path.join(base_dir, "dynamic_blacklist.txt")

        # Connect
        self.analyze_btn.clicked.connect(self.on_analyze_clicked)
        copy_btn.clicked.connect(self.copy_report)
        clear_btn.clicked.connect(self.clear_input)

        if parent:
            home_btn.clicked.connect(lambda: parent.display_page("landing"))
            about_btn.clicked.connect(lambda: parent.display_page("about"))
            help_btn.clicked.connect(lambda: parent.display_page("help"))

    # ----------------- Normalization & Validation ----------------- #
    def normalize_url(self, url: str) -> str:
        """
        Return a canonical URL string:
         - strip whitespace,
         - add default scheme (http) if missing,
         - normalize scheme/host to lowercase,
         - remove fragment, trim trailing slash in path.
        """
        url = (url or "").strip()
        if not url:
            return ""
        # Add scheme if missing
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', url):
            url = "http://" + url

        parts = urllib.parse.urlsplit(url)
        scheme = (parts.scheme or "http").lower()
        netloc = (parts.netloc or "").lower()

        if "@" in netloc:
            netloc = netloc.split("@")[-1]

        path = parts.path.rstrip('/')
        if path == "/":
            path = ""
        query = parts.query
        normalized = urllib.parse.urlunsplit((scheme, netloc, path, query, ""))
        return normalized

    def get_domain(self, url: str) -> str:
        """Extract hostname (domain) from a URL after normalization. Returns lowercase hostname."""
        try:
            normalized = self.normalize_url(url)
            parsed = urllib.parse.urlsplit(normalized)
            host = parsed.hostname or ""
            return host.lower()
        except Exception:
            return ""

    def is_valid_url(self, url: str) -> bool:
        """Validate URL structure with scheme and hostname checks (allows IP addresses)."""
        try:
            normalized = self.normalize_url(url)
            if not normalized:
                return False
            parsed = urllib.parse.urlsplit(normalized)
            scheme = (parsed.scheme or "").lower()
            if scheme not in ("http", "https", "ftp"):
                return False
            host = parsed.hostname
            if not host:
                return False

            # If host is an IP address -> valid
            try:
                ipaddress.ip_address(host)
                return True
            except ValueError:
                pass  # not an IP; continue to hostname validation

            if '.' not in host:
                return False
            if len(host.split('.')[-1]) < 2 and not host.startswith("xn--"):
                return False

            if not re.match(r'^[A-Za-z0-9\.\-]+$', host):
                return False

            return True
        except Exception:
            return False

    def domain_exists(self, url: str):
        """
        Check DNS resolution for the domain.
        Returns:
          True  -> domain resolved to an IP (likely exists)
          False -> domain likely does not exist (NXDOMAIN)
          None  -> temporary DNS/network error or unable to determine
        """
        domain = self.get_domain(url)
        if not domain:
            return False

        try:
            ipaddress.ip_address(domain)
            return True
        except ValueError:
            pass

        try:
            socket.getaddrinfo(domain, None)
            return True
        except socket.gaierror as e:
            emsg = str(e).lower()
            if ("name or service not known" in emsg
                    or "nodename nor servname provided" in emsg
                    or "no address associated" in emsg
                    or "eai_noname" in emsg):
                return False
            if ("temporary failure" in emsg
                    or "try again" in emsg
                    or "eai_again" in emsg
                    or "timed out" in emsg):
                return None
            return None
        except Exception:
            return None

    # ----------------- File helpers ----------------- #
    def load_urls_from_file(self, filename: str) -> set:
        """
        Load a file and return a set containing:
         - domain-only entries
         - normalized URL entries (if file contains full URL)
        This makes comparisons robust against either 'example.com' or 'http://example.com' in files.
        """
        entries = set()
        if not os.path.exists(filename):
            return entries
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if not s:
                        continue
                    s_low = s.lower()
                    # If looks like a URL or contains a slash, normalize to canonical URL and domain
                    if re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', s_low) or '/' in s_low:
                        try:
                            norm = self.normalize_url(s_low)
                            entries.add(norm)
                            host = self.get_domain(norm)
                            if host:
                                entries.add(host)
                        except Exception:
                            entries.add(s_low)
                    else:
                        # domain-only entry
                        entries.add(s_low)
        except Exception:
            # if file read fails, return empty set
            return set()
        return entries

    def save_to_dynamic_blacklist(self, url: str):
        """
        Save domain (preferred) to dynamic blacklist; avoid duplicates.
        """
        domain = self.get_domain(url) or url.lower()
        existing = self.load_urls_from_file(self.dynamic_blacklist_file)
        if domain.lower() in existing:
            return
        try:
            with open(self.dynamic_blacklist_file, "a", encoding="utf-8") as f:
                f.write(domain.lower() + "\n")
        except Exception:
            pass

    def heuristic_check(self, url: str) -> bool:
        suspicious_keywords = ["scam", "phish", "login", "verify", "bank", "update"]
        if any(word in url.lower() for word in suspicious_keywords):
            return True
        if len(url) > 75:
            return True
        if "@" in url:
            return True
        if url.count("//") > 1:
            return True
        return False

    # ---------------- Main Analysis (UI-facing function) ---------------- #
    def analyze_url(self):
        """
        UI-facing (synchronous) analysis function — kept for completeness but main flow uses threaded worker.
        """
        raw = self.url_input.text().strip()
        if not raw:
            self.reasons_box.setPlainText("Please enter a URL to analyze.")
            self.risk_score_box.setText("0%")
            self.result_status_label.setText("Result: --")
            self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: black;")
            return

        url = self.normalize_url(raw)
        if not self.is_valid_url(url):
            self.risk_score_box.setText("80%")
            self.result_status_label.setText("Result: ⚠️ INVALID URL")
            self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: orange;")
            self.risk_score_box.setStyleSheet("font-size: 20px; font-weight: bold; color: orange;")
            self.reasons_box.setPlainText(
                f"The entered URL '{raw}' is not properly formatted.\n\n"
                "Please check the URL. If you believe this is a phishing URL you can add it to the blacklist."
            )
            self.ask_add_to_list(url, "blacklist")
            return

        domain = self.get_domain(url)
        whitelist = self.load_urls_from_file(self.whitelist_file)
        blacklist = self.load_urls_from_file(self.blacklist_file)
        dynamic = self.load_urls_from_file(self.dynamic_blacklist_file)

        # Whitelist
        if (domain and domain in whitelist) or (url.lower() in whitelist):
            self.risk_score_box.setText("0%")
            self.result_status_label.setText("Result: ✅ SAFE (Whitelisted)")
            self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: green;")
            self.risk_score_box.setStyleSheet("font-size: 20px; font-weight: bold; color: green;")
            self.reasons_box.setPlainText(f"The URL '{raw}' is in the whitelist.\n\n✅ Trusted website.")
            return

        # Blacklist
        if (domain and domain in blacklist) or (url.lower() in blacklist):
            self.risk_score_box.setText("100%")
            self.result_status_label.setText("Result: ❌ BLACKLISTED URL")
            self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: red;")
            self.risk_score_box.setStyleSheet("font-size: 20px; font-weight: bold; color: red;")
            self.reasons_box.setPlainText(f"The URL '{raw}' is in the blacklist.\n\n❌ Confirmed malicious.")
            return

        # Dynamic blacklist
        if (domain and domain in dynamic) or (url.lower() in dynamic):
            self.risk_score_box.setText("95%")
            self.result_status_label.setText("Result: ⚠️ DYNAMIC BLACKLISTED")
            self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: red;")
            self.risk_score_box.setStyleSheet("font-size: 20px; font-weight: bold; color: red;")
            self.reasons_box.setPlainText(f"The URL '{raw}' was flagged earlier and is now in dynamic blacklist.")
            return

        # Heuristic
        if self.heuristic_check(url):
            self.save_to_dynamic_blacklist(url)
            self.risk_score_box.setText("90%")
            self.result_status_label.setText("Result: ⚠️ PHISHING/SCAM (Heuristic)")
            self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: red;")
            self.risk_score_box.setStyleSheet("font-size: 20px; font-weight: bold; color: red;")
            self.reasons_box.setPlainText(
                f"The URL '{raw}' looks suspicious based on heuristic rules.\n\n"
                f"- Added to dynamic blacklist.\n- Possible phishing attempt."
            )
            self.ask_add_to_list(url, "blacklist")
            return

        # DNS / Domain check
        dns_ok = self.domain_exists(url)
        if dns_ok is True:
            pass
        elif dns_ok is None:
            self.risk_score_box.setText("10%")
            self.result_status_label.setText("Result: ⚠️ UNKNOWN (Could not verify domain)")
            self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: orange;")
            self.reasons_box.setPlainText(
                f"Could not verify the domain for '{raw}'.\n\nThis may be a network or DNS issue. Please check your internet connection and try again."
            )
            return
        else:
            self.save_to_dynamic_blacklist(url)
            self.risk_score_box.setText("85%")
            self.result_status_label.setText("Result: ❌ NON-EXISTENT DOMAIN")
            self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: orange;")
            self.risk_score_box.setStyleSheet("font-size: 20px; font-weight: bold; color: orange;")
            self.reasons_box.setPlainText(f"The domain in '{raw}' does not exist.\n\n❌ Added to dynamic blacklist.")
            self.ask_add_to_list(url, "blacklist")
            return

        # Safe
        self.risk_score_box.setText("5%")
        self.result_status_label.setText("Result: ✅ SAFE URL")
        self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: green;")
        self.risk_score_box.setStyleSheet("font-size: 20px; font-weight: bold; color: green;")
        self.reasons_box.setPlainText(f"The URL '{raw}' passed all checks.\n\n✅ Likely safe to use.")
        self.ask_add_to_list(url, "whitelist")

    # ----------------- Ask to add ----------------- #
    def ask_add_to_list(self, url: str, list_type: str):
        """
        Ask user to add URL/domain to whitelist or blacklist.
        Stores domain if available (preferred).
        """
        file = self.blacklist_file if list_type == "blacklist" else self.whitelist_file
        existing = self.load_urls_from_file(file)

        domain = self.get_domain(url)
        display_target = domain if domain else url

        if display_target.lower() in existing:
            QMessageBox.information(self, "Already present", f"The URL/domain is already in the {list_type}.")
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Add URL Confirmation")
        if list_type == "blacklist":
            msg.setText(f"⚠️ The URL\n{url}\nseems unsafe.\nDo you want to add it to the blacklist?")
            msg.setIcon(QMessageBox.Warning)
            yes_btn = msg.addButton("Yes, add to blacklist", QMessageBox.YesRole)
        else:
            msg.setText(f"✅ The URL\n{url}\nlooks safe.\nDo you want to add it to the whitelist?")
            msg.setIcon(QMessageBox.Information)
            yes_btn = msg.addButton("Yes, add to whitelist", QMessageBox.YesRole)

        msg.addButton("Cancel", QMessageBox.RejectRole)
        msg.exec_()

        if msg.clickedButton() == yes_btn:
            to_write = domain if domain else url.lower()
            if to_write.lower() in existing:
                QMessageBox.information(self, "Already present", f"The URL/domain is already in the {list_type}.")
            else:
                try:
                    with open(file, "a", encoding="utf-8") as f:
                        f.write(to_write.lower() + "\n")
                    QMessageBox.information(self, "Added", f"{to_write} added to {list_type}.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to write to file: {e}")

    # ----------------- Copy / Clear ----------------- #
    def copy_report(self):
        report = (
            f"URL: {self.url_input.text()}\n"
            f"Risk Score: {self.risk_score_box.text()}\n"
            f"Result: {self.result_status_label.text().replace('Result: ', '')}\n\n"
            f"Reasons:\n{self.reasons_box.toPlainText()}"
        )
        clipboard = QApplication.clipboard()
        clipboard.setText(report)
        QMessageBox.information(self, "Copied", "Report copied to clipboard!")

    def clear_input(self):
        """Clear URL input and reset UI elements."""
        self.url_input.clear()
        self.reasons_box.clear()
        self.risk_score_box.setText("0%")
        self.result_status_label.setText("Result: --")
        self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: black;")

    # ---------------- Loading UI and threaded execution ---------------- #
    def _create_loading_widgets(self):
        """
        Create a QLabel with QMovie (spinner.gif) and a fallback indeterminate QProgressBar.
        """
        self.loading_label = QLabel(self)
        self.loading_label.setVisible(False)

        spinner_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "spinner.gif")
        if os.path.exists(spinner_path):
            try:
                self.loading_movie = QMovie(spinner_path)
                if self.loading_movie.isValid():
                    self.loading_label.setMovie(self.loading_movie)
                else:
                    self.loading_movie = None
            except Exception:
                self.loading_movie = None
        else:
            self.loading_movie = None

        self.loading_progress = QProgressBar(self)
        self.loading_progress.setRange(0, 0)  # indeterminate
        self.loading_progress.setVisible(False)
        self.loading_progress.setFixedHeight(12)

        # Add to layout at the bottom region
        if self.layout() is not None:
            self.layout().addWidget(self.loading_label)
            self.layout().addWidget(self.loading_progress)

    def _start_loading_ui(self):
        try:
            self.analyze_btn.setEnabled(False)
        except Exception:
            pass

        if getattr(self, "loading_movie", None):
            self.loading_label.setVisible(True)
            try:
                self.loading_movie.start()
            except Exception:
                pass
            self.loading_progress.setVisible(False)
        else:
            self.loading_label.setVisible(False)
            self.loading_progress.setVisible(True)

    def _stop_loading_ui(self):
        if getattr(self, "loading_movie", None):
            try:
                self.loading_movie.stop()
            except Exception:
                pass
            self.loading_label.setVisible(False)
        self.loading_progress.setVisible(False)
        try:
            self.analyze_btn.setEnabled(True)
        except Exception:
            pass

    # ---------------- Threaded analysis ---------------- #
    def on_analyze_clicked(self):
        """
        Starts spinner and runs `perform_blocking_analysis` in a background thread.
        """
        raw = self.url_input.text().strip()
        if not raw:
            QMessageBox.warning(self, "Input required", "Please enter a URL to analyze.")
            return

        self._start_loading_ui()

        worker = AnalysisWorker(self.perform_blocking_analysis, raw)
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(self._on_analysis_finished)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        worker.error.connect(self._on_analysis_error)
        worker.error.connect(thread.quit)
        worker.error.connect(worker.deleteLater)

        self._current_analysis_thread = thread
        self._current_analysis_worker = worker

        thread.start()

    def perform_blocking_analysis(self, raw_url: str) -> dict:
        url = self.normalize_url(raw_url)
        if not self.is_valid_url(url):
            return {
                "url": url,
                "verdict": "invalid",
                "risk": 80,
                "notes": "Invalid URL format",
                "suggest_add": None
            }

        whitelist = self.load_urls_from_file(self.whitelist_file)
        blacklist = self.load_urls_from_file(self.blacklist_file)
        dynamic = self.load_urls_from_file(self.dynamic_blacklist_file)
        domain = self.get_domain(url)

        # Already whitelisted
        if (domain and domain in whitelist) or (url.lower() in whitelist):
            return {"url": url, "verdict": "safe", "risk": 0, "notes": "Whitelisted", "suggest_add": None}

        # Already blacklisted
        if (domain and domain in blacklist) or (url.lower() in blacklist):
            return {"url": url, "verdict": "blacklisted", "risk": 100, "notes": "Listed in blacklist", "suggest_add": None}

        # Already in dynamic
        if (domain and domain in dynamic) or (url.lower() in dynamic):
            return {"url": url, "verdict": "dynamic", "risk": 95, "notes": "Listed in dynamic blacklist", "suggest_add": None}

        # Heuristic suspicious -> suggest adding to blacklist
        if self.heuristic_check(url):
            try:
                self.save_to_dynamic_blacklist(url)
            except Exception:
                pass
            return {
                "url": url,
                "verdict": "suspicious",
                "risk": 90,
                "notes": "Heuristic rules matched. Consider blocking.",
                "suggest_add": "blacklist"
            }

        # DNS check: if domain does not resolve, mark suspicious (existing behaviour)
        dns_ok = self.domain_exists(url)
        if dns_ok is False:
            try:
                self.save_to_dynamic_blacklist(url)
            except Exception:
                pass
            return {
                "url": url,
                "verdict": "nonexistent",
                "risk": 85,
                "notes": "Domain does not resolve.",
                "suggest_add": "blacklist"
            }
        elif dns_ok is None:
            # Could not verify DNS (network issue) — leave inconclusive
            return {
                "url": url,
                "verdict": "unknown",
                "risk": 10,
                "notes": "Could not verify domain (DNS/network issue).",
                "suggest_add": None
            }

        # At this point DNS exists (domain resolves) — check WHOIS / registration status
        # NOTE: is_domain_registered does network I/O; we are in a background thread, so it's ok.
        registered = self.is_domain_registered(domain)
        if registered is False:
            # Domain explicitly appears unregistered -> suspicious
            try:
                self.save_to_dynamic_blacklist(url)
            except Exception:
                pass
            return {
                "url": url,
                "verdict": "unregistered",
                "risk": 90,
                "notes": "WHOIS indicates domain is not registered (available). Possibly malicious.",
                "suggest_add": "blacklist"
            }
        elif registered is None:
            # Inconclusive WHOIS — continue and consider safe if no other flags
            # but mark note so user knows registration couldn't be confirmed
            return {
                "url": url,
                "verdict": "unknown_registration",
                "risk": 15,
                "notes": "DNS resolves but WHOIS lookup was inconclusive. Proceed with caution.",
                "suggest_add": None
            }

        # If registered is True -> domain is registered and DNS resolved, so consider safe by default
        return {
            "url": url,
            "verdict": "safe",
            "risk": 5,
            "notes": "Passed checks; domain resolves and appears registered.",
            "suggest_add": "whitelist"
        }

    def _on_analysis_finished(self, result):

        self._stop_loading_ui()
        try:
            if isinstance(result, dict):
                url = result.get("url", "")
                risk = result.get("risk", 0)
                verdict = result.get("verdict", "unknown")
                notes = result.get("notes", "")
                suggest = result.get("suggest_add", None)

                self.risk_score_box.setText(f"{risk}%")

                # Set result label style by verdict
                if verdict == "safe":
                    self.result_status_label.setText("Result: ✅ SAFE URL")
                    self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: green;")
                    self.risk_score_box.setStyleSheet("font-size: 20px; font-weight: bold; color: green;")
                elif verdict in ("blacklisted", "dynamic"):
                    self.result_status_label.setText("Result: ❌ BLACKLISTED URL")
                    self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: red;")
                    self.risk_score_box.setStyleSheet("font-size: 20px; font-weight: bold; color: red;")
                elif verdict in ("suspicious", "invalid", "nonexistent"):
                    label_text = "Result: ⚠️ " + verdict.upper()
                    self.result_status_label.setText(label_text)
                    self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: orange;")
                    self.risk_score_box.setStyleSheet("font-size: 20px; font-weight: bold; color: orange;")
                else:
                    self.result_status_label.setText("Result: ⚠️ UNKNOWN")
                    self.result_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: orange;")

                self.reasons_box.setPlainText(notes)

                # If worker suggests adding, prompt user (main thread)
                if suggest in ("blacklist", "whitelist") and url:
                    # Use normalized URL for storage but you can show the raw input by replacing url with self.url_input.text().strip()
                    self.ask_add_to_list(url, suggest)

            else:
                # If not dict, just show textual result
                self.reasons_box.setPlainText(str(result))
        except Exception as e:
            # fallback: show what we have
            QMessageBox.information(self, "Analysis result", f"{result}\n\nException: {e}")

        # clean up references
        self._current_analysis_thread = None
        self._current_analysis_worker = None


    def _on_analysis_error(self, err_msg):
        self._stop_loading_ui()
        QMessageBox.critical(self, "Analysis error", f"An error occurred: {err_msg}")
        self._current_analysis_thread = None
        self._current_analysis_worker = None


    def is_domain_registered(self, domain: str, timeout: int = 6):
        if not domain:
            return None
        # Treat IPs as "registered"
        try:
            ipaddress.ip_address(domain)
            return True
        except Exception:
            pass

        tld = domain.rsplit(".", 1)[-1].lower() if "." in domain else ""
        # servers that commonly respond for particular TLDs
        whois_servers = {
            "com": "whois.verisign-grs.com",
            "net": "whois.verisign-grs.com",
            "org": "whois.pir.org",
            "info": "whois.afilias.net",
            "io": "whois.nic.io",
            "co": "whois.nic.co",
            "in": "whois.registry.in",
            "me": "whois.nic.me",
            "biz": "whois.biz",
            "us": "whois.nic.us",
            "uk": "whois.nic.uk",
        }

        servers_to_try = []
        if tld and tld in whois_servers:
            servers_to_try.append(whois_servers[tld])
        # useful fallback servers
        servers_to_try.extend(["whois.iana.org", "whois.crsnic.net", "whois.verisign-grs.com"])

        for server in servers_to_try:
            try:
                s = socket.create_connection((server, 43), timeout=timeout)
                s.settimeout(timeout)
                # Some WHOIS servers for .com/net require the prefix "domain " or just domain; sending domain is fine.
                query = domain + "\r\n"
                s.send(query.encode("utf-8", errors="ignore"))
                resp = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    resp += chunk
                s.close()
                text = resp.decode("utf-8", errors="ignore").lower()

                # common markers for "not found / available"
                not_found_markers = [
                    "no match for",
                    "not found",
                    "no data found",
                    "no entries found",
                    "status: available",
                    "domain not found",
                    "no such domain",
                    "available",
                ]
                for m in not_found_markers:
                    if m in text:
                        return False

                # common markers for "registered"
                registered_markers = [
                    "domain name:",
                    "registrar:",
                    "creation date",
                    "registered on",
                    "registry expiry date",
                    "expiry date",
                    "updated date",
                    "registration date",
                ]
                for m in registered_markers:
                    if m in text:
                        return True

                # if server returned other content but no clear marker - try next server
                continue
            except Exception:
                # try next server
                continue

        # if all servers tried but none gave a conclusive answer, return None (inconclusive)
        return None



# ---------------- About Page ---------------- #
class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        title = QLabel("ℹ️ About Us", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        text = QLabel("This project helps detect phishing URLs.\nDeveloped by our team for cybersecurity awareness.")
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("font-size: 16px;")

        back_btn = QPushButton("Home")
        back_btn.clicked.connect(lambda: parent.display_page("landing") if parent else None)
        back_btn.setFixedSize(160, 50)
        back_btn.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                background-color: #2E86C1;
                color: white;
                border-radius: 8px;
            """)
        back_layout = QHBoxLayout()
        back_layout.addStretch()
        back_layout.addWidget(back_btn)
        back_layout.addStretch()

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addStretch(1)
        layout.addLayout(back_layout)
        self.setLayout(layout)


# ---------------- Help Page ---------------- #
class HelpPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        title = QLabel("❓ Help", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        text = QLabel("1. Paste a URL in the analyzer.\n2. Click 'Analyze' to check risk score.\n3. Copy report for further details.\n4. Use 'Clear' to reset the input.")
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("font-size: 16px;")

        back_btn = QPushButton("Home")
        back_btn.clicked.connect(lambda: parent.display_page("landing") if parent else None)
        back_btn.setFixedSize(160, 50)
        back_btn.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                background-color: #2E86C1;
                color: white;
                border-radius: 8px;
            """)
        back_layout = QHBoxLayout()
        back_layout.addStretch()
        back_layout.addWidget(back_btn)
        back_layout.addStretch()

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addStretch(1)
        layout.addLayout(back_layout)
        self.setLayout(layout)


# ---------------- Main Window ---------------- #
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phishing Detection App")
        self.setGeometry(100, 100, 1100, 700)
        self.display_page("landing")

    def display_page(self, page_name: str):
        if page_name == "landing":
            self.setCentralWidget(LandingPage(self))
        elif page_name == "analyzer":
            self.setCentralWidget(AnalyzerPage(self))
        elif page_name == "about":
            self.setCentralWidget(AboutPage(self))
        elif page_name == "help":
            self.setCentralWidget(HelpPage(self))


# ---------------- Run App ---------------- #
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

