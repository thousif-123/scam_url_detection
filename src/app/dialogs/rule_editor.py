from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

class RuleEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rule Editor")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is the Rule Editor (functionality coming soon)."))
        self.setLayout(layout)
