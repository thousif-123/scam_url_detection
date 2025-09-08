from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

class LogsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Logs")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is the Logs viewer (functionality coming soon)."))
        self.setLayout(layout)
