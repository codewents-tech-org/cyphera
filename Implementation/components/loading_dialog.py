from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from models import Parameters as P  # Import loader path

class RoundLoader(QDialog):
    """White Box Loader with Transparent Image"""
    
    def __init__(self, parent=None, label_text = ''):
        super().__init__(parent)

        # **White Box Background (No Shadows, No Borders)**
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
            border: none;  /* Ensure no grey border */
        """)
        self.setFixedSize(400, 250)  # White box size
        self.setModal(True)  # Blocks UI interactions

        # **Layout Setup (No Extra Spacing)**
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)  # Reduce margin
        layout.setSpacing(0)  # Prevent extra space

        # **Use QLabel Instead of QSvgWidget**
        self.image_label = QLabel(self)
        pixmap = QPixmap(P.loader_icon)  # Load the image
        self.image_label.setPixmap(pixmap.scaled(170, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background: transparent;
            border: none;
        """)  # Ensure full transparency
        # **Loading Text Label**
        self.text_label = QLabel(label_text, self)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("font-size: 14px; color: black;")

        # **Add Widgets to Layout**
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.text_label, alignment=Qt.AlignCenter)

# To test the loader
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    loader = RoundLoader()
    loader.show()
    sys.exit(app.exec_())
