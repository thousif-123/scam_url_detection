from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel
from app.dialogs.blacklist import BlacklistDialog
from app.dialogs.watchlist import WatchlistDialog
from app.dialogs.rule_editor import RuleEditorDialog
from app.dialogs.settings import SettingsDialog
from app.dialogs.logs import LogsDialog


# Temporary placeholder dialog (until real dialogs are created)
class PlaceholderDialog(QDialog):
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


class UIController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.connect_ui()

    def connect_ui(self):
        # Connect input and button
        self.main_window.check_btn.clicked.connect(self.check_url)
        self.main_window.url_input.returnPressed.connect(self.check_url)

        # Connect menus
        self.main_window.open_blacklist_action.triggered.connect(self.open_blacklist)
        self.main_window.open_watchlist_action.triggered.connect(self.open_watchlist)
        self.main_window.open_rule_editor_action.triggered.connect(self.open_rule_editor)
        self.main_window.open_settings_action.triggered.connect(self.open_settings)
        self.main_window.open_logs_action.triggered.connect(self.open_logs)
        self.main_window.about_action.triggered.connect(self.show_about)

    def check_url(self):
        url = self.main_window.url_input.text().strip()

        if not url:
            QMessageBox.warning(self.main_window, "Missing URL", "Please enter a URL to check.")
            return

        self.main_window.statusBar().showMessage("Checking...")
        self.main_window.check_btn.setEnabled(False)

        # Dummy result until heuristics are implemented
        result = {
            "url": url,
            "score": 0,
            "verdict": "Safe",
            "matched_rules": []
        }

        if hasattr(self.main_window, "display_result"):
            self.main_window.display_result(result)

        self.main_window.check_btn.setEnabled(True)
        self.main_window.statusBar().showMessage("Check complete.")

    # Menu actions (using placeholder dialogs for now)
    def open_blacklist(self):
        dialog = BlacklistDialog(self.main_window)
        dialog.exec_()

    def open_watchlist(self):
        dialog = WatchlistDialog(self.main_window)
        dialog.exec_()

    def open_rule_editor(self):
        dialog = RuleEditorDialog(self.main_window)
        dialog.exec_()

    def open_settings(self):
        dialog = SettingsDialog(self.main_window)
        dialog.exec_()

    def open_logs(self):
        dialog = LogsDialog(self.main_window)
        dialog.exec_()


    def show_about(self):
        QMessageBox.information(
            self.main_window,
            "About",
            "Fake URL Detector - GUI skeleton\nDialogs not implemented yet."
        )
