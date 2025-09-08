from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is the Settings dialog (functionality coming soon)."))
        self.setLayout(layout)
