from PySide6.QtWidgets import QApplication, QLabel

app = QApplication([])

label = QLabel("Hello, Linux GUI!")
label.show()

app.exec()