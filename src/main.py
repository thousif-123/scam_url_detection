#!/usr/bin/env python3


import sys
import datetime

# Try to import PyQt5; if it's missing, we'll fall back to a safe CLI mode.
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLineEdit, QPushButton, QLabel, QListWidget, QStatusBar,
        QAction, QDialog, QMessageBox
    )
    from PyQt5.QtCore import Qt
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False


# ---------------------------
# CLI fallback (when PyQt5 is not installed)
# ---------------------------
def main_cli():
    """Simple command-line fallback for environments without PyQt5."""
    print("=" * 60)
    print("Fake URL Detector - GUI not available (PyQt5 not installed).")
    print("To run the GUI, install PyQt5: python3 -m pip install PyQt5")
    print("This CLI will simulate a URL check so you can verify the script runs.")
    print("=" * 60)
    try:
        while True:
            url = input("Enter a URL to 'check' (or type 'quit'): ").strip()
            if not url:
                continue
            if url.lower() in ("quit", "q", "exit"):
                print("Exiting CLI. Install PyQt5 to run the GUI.")
                break
            # Simulated placeholder result:
            print(f"\nSimulated check for: {url}")
            print("Score: 0")
            print("Verdict: Safe (placeholder)\n")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting. Bye.")


# If PyQt5 is not available, don't define GUI classes; we'll use CLI.
if PYQT5_AVAILABLE:
    # ---------------------------
    # Placeholder Dialog: reuse for simple "coming soon" windows
    # ---------------------------
    class PlaceholderDialog(QDialog):
        """A small dialog used as a placeholder for future dialogs."""
        def __init__(self, title: str, parent=None):
            super().__init__(parent)
            self.setWindowTitle(title)
            self.resize(600, 320)
            layout = QVBoxLayout(self)
            label = QLabel(
                f"This is a placeholder for the '{title}' dialog.\n\n"
                "Functionality will be added later."
            )
            label.setWordWrap(True)
            layout.addWidget(label)

    # ---------------------------
    # Main application window (skeleton)
    # ---------------------------
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fake URL Detector")
            self.resize(900, 560)
            self._build_ui()
            self._create_actions()
            self._create_menu()
            self.statusBar().showMessage("Ready")

        def _build_ui(self):
            """Construct the central widgets and layout."""
            central = QWidget()
            self.setCentralWidget(central)
            vbox = QVBoxLayout(central)

            # --- Input row ---
            h_input = QHBoxLayout()
            self.url_input = QLineEdit()
            self.url_input.setPlaceholderText("Enter URL to check (e.g., https://example.com/login)")
            # Support pressing Enter to trigger check:
            self.url_input.returnPressed.connect(self.on_check_clicked)

            self.check_btn = QPushButton("Check")
            self.check_btn.clicked.connect(self.on_check_clicked)
            h_input.addWidget(self.url_input)
            h_input.addWidget(self.check_btn)
            vbox.addLayout(h_input)

            # --- Result row ---
            h_result = QHBoxLayout()
            self.risk_badge = QLabel("Not checked")
            self.risk_badge.setAlignment(Qt.AlignCenter)
            self.risk_badge.setFixedWidth(140)
            self.risk_badge.setStyleSheet("background-color: lightgray; padding: 6px; border-radius: 8px;")
            self.score_label = QLabel("Score: -")
            h_result.addWidget(self.risk_badge)
            h_result.addWidget(self.score_label)
            h_result.addStretch()
            vbox.addLayout(h_result)

            # --- Matched rules list ---
            self.rules_list = QListWidget()
            self.rules_list.addItem("Matched rules will appear here after checking a URL.")
            vbox.addWidget(self.rules_list)

            # --- Quick actions (disabled placeholders) ---
            h_actions = QHBoxLayout()
            self.add_blacklist_btn = QPushButton("Add to blacklist")
            self.add_blacklist_btn.setEnabled(False)  # disabled until we have real logic
            self.report_fp_btn = QPushButton("Report false positive")
            self.report_fp_btn.setEnabled(False)
            h_actions.addWidget(self.add_blacklist_btn)
            h_actions.addWidget(self.report_fp_btn)
            h_actions.addStretch()
            vbox.addLayout(h_actions)

        def _create_actions(self):
            """Create reusable QAction objects used in the menu."""
            self.exit_action = QAction("Exit", self)
            self.exit_action.triggered.connect(self.close)

            self.open_blacklist_action = QAction("Blacklist Manager", self)
            self.open_blacklist_action.triggered.connect(self.open_blacklist_manager)

            self.open_watchlist_action = QAction("Watchlist", self)
            self.open_watchlist_action.triggered.connect(self.open_watchlist)

            self.open_rule_editor_action = QAction("Rule Editor", self)
            self.open_rule_editor_action.triggered.connect(self.open_rule_editor)

            self.open_settings_action = QAction("Settings", self)
            self.open_settings_action.triggered.connect(self.open_settings)

            self.open_logs_action = QAction("Logs", self)
            self.open_logs_action.triggered.connect(self.open_logs)

            self.about_action = QAction("About", self)
            self.about_action.triggered.connect(self.show_about)

        def _create_menu(self):
            """Build the menu bar and attach actions."""
            menubar = self.menuBar()
            file_menu = menubar.addMenu("File")
            file_menu.addAction(self.exit_action)

            tools_menu = menubar.addMenu("Tools")
            tools_menu.addAction(self.open_blacklist_action)
            tools_menu.addAction(self.open_watchlist_action)
            tools_menu.addAction(self.open_rule_editor_action)

            admin_menu = menubar.addMenu("Admin")
            admin_menu.addAction(self.open_settings_action)
            admin_menu.addAction(self.open_logs_action)

            help_menu = menubar.addMenu("Help")
            help_menu.addAction(self.about_action)

        # ---------------------------
        # Core stub callbacks (to be wired to real logic later)
        # ---------------------------
        def on_check_clicked(self):
            """Called when the user clicks 'Check' (or presses Enter)."""
            url = self.url_input.text().strip()
            if not url:
                QMessageBox.warning(self, "Input required", "Please enter a URL to check.")
                return

            # UI feedback while "checking" (placeholder)
            self.statusBar().showMessage("Checking...")
            self.check_btn.setEnabled(False)
            QApplication.processEvents()  # let the UI update

            # Placeholder evaluator — replace this with the real heuristics engine later
            result = self.evaluate_url_stub(url)

            # Display results in the UI
            self.display_result(result)

            # re-enable controls and update status
            self.check_btn.setEnabled(True)
            self.statusBar().showMessage(f"Last checked: {datetime.datetime.now().isoformat(timespec='seconds')}")

        def evaluate_url_stub(self, url: str) -> dict:
            """
            Placeholder evaluation function.
            Return format:
                {
                    "url": str,
                    "score": int,
                    "verdict": "Safe"|"Suspicious"|"Malicious",
                    "matched_rules": [ { "rule": name, "explanation": text, "weight": n }, ... ]
                }
            """
            # Simple default: everything safe with score 0
            return {
                "url": url,
                "score": 0,
                "verdict": "Safe",
                "matched_rules": []
            }

        def display_result(self, result: dict):
            """Update UI widgets based on the evaluator result dict."""
            score = result.get("score", 0)
            verdict = result.get("verdict", "Unknown")
            self.score_label.setText(f"Score: {score}")
            self.risk_badge.setText(verdict)

            # Color the badge - keep colors simple and readable:
            v = verdict.lower()
            if v == "safe":
                color = "#8fbc8f"  # greenish
            elif v == "suspicious":
                color = "#f2d26a"  # yellowish
            else:
                color = "#f08080"  # reddish

            self.risk_badge.setStyleSheet(f"background-color: {color}; padding: 6px; border-radius: 8px;")

            # Update matched rules list
            self.rules_list.clear()
            matches = result.get("matched_rules", [])
            if not matches:
                self.rules_list.addItem("No matched rules.")
                self.add_blacklist_btn.setEnabled(False)
                self.report_fp_btn.setEnabled(False)
            else:
                for r in matches:
                    name = r.get("rule", "Unnamed rule")
                    explanation = r.get("explanation", "")
                    self.rules_list.addItem(f"{name}: {explanation}")
                self.add_blacklist_btn.setEnabled(True)
                self.report_fp_btn.setEnabled(True)

        # ---------------------------
        # Dialog openers (placeholders)
        # ---------------------------
        def open_blacklist_manager(self):
            dlg = PlaceholderDialog("Blacklist Manager", self)
            dlg.exec_()

        def open_watchlist(self):
            dlg = PlaceholderDialog("Watchlist / Review Queue", self)
            dlg.exec_()

        def open_rule_editor(self):
            dlg = PlaceholderDialog("Rule Editor", self)
            dlg.exec_()

        def open_settings(self):
            dlg = PlaceholderDialog("Settings", self)
            dlg.exec_()

        def open_logs(self):
            dlg = PlaceholderDialog("Logs", self)
            dlg.exec_()

        def show_about(self):
            QMessageBox.information(self, "About", "Fake URL Detector - GUI skeleton\nNo heuristics implemented yet.")


# ---------------------------
# Main entrypoint
# ---------------------------
def main():
    if PYQT5_AVAILABLE:
        app = QApplication(sys.argv)
        win = MainWindow()
        win.show()
        sys.exit(app.exec_())
    else:
        main_cli()


if __name__ == "__main__":
    main()
