from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

class BlacklistDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Blacklist Manager")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is the Blacklist Manager (functionality coming soon)."))
        self.setLayout(layout)
