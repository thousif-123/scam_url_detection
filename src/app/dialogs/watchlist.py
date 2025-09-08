from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

class WatchlistDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Watchlist")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is the Watchlist (functionality coming soon)."))
        self.setLayout(layout)
