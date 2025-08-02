from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer ,QSize
from PyQt5.QtGui import QMovie
from models import Parameters as P  # loader_gif path

class RoundLoader(QDialog):
    """Circular Animated Loader in a White Box"""
    
    def __init__(self, parent=None, label_text='Loading...'):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
        """)
        self.setFixedSize(300, 200)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Animated loader using GIF
        self.loader_label = QLabel(self)
        self.loader_label.setAlignment(Qt.AlignCenter)
        self.movie = QMovie(P.loader_gif)
        self.movie.setScaledSize(QSize(64, 64))  # Adjust as needed
        self.loader_label.setMovie(self.movie)
        self.movie.start()

        # Optional text
        self.text_label = QLabel(label_text, self)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("font-size: 14px; color: black;")

        layout.addWidget(self.loader_label)
        layout.addWidget(self.text_label)

# Test block
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    loader = RoundLoader(label_text="Please wait...")
    loader.show()
    QTimer.singleShot(3000, loader.close)  # Auto-close after 3 seconds
    sys.exit(app.exec_())
