from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import sys
import os

# Adjust sys.path to include the Implementation directory
current_dir = os.path.dirname(os.path.abspath(__file__))
implementation_dir = os.path.abspath(os.path.join(current_dir, '../../../'))
assets_dir = os.path.join(current_dir, "../../../../Implementation/assets/images/")

if implementation_dir not in sys.path:
    sys.path.insert(0, implementation_dir)

# Import styles
from styles.license_panel_style import (
   STYLE_SHEET
)


class LicenseRenewalPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(STYLE_SHEET["main"])
        self.initUI()

    def initUI(self):
        # Main layout for the entire panel
        outer_layout = QVBoxLayout(self)  # Outer layout to center content
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.setAlignment(Qt.AlignCenter)

        # Container widget for fixed-width content
        container_widget = QWidget()
        container_widget.setFixedSize(1350, 700)  # Fixed width for both panels combined
        container_layout = QHBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)  # No margins inside the container
        container_layout.setSpacing(0)  # No spacing between the panels

        # Left Panel
        left_panel_widget = QWidget()
        left_panel_widget.setFixedSize(900, 700)  # Fixed size for the left panel
        left_panel_widget.setStyleSheet(STYLE_SHEET["left_panel"])

        # Layout for the left panel
        left_panel_layout = QVBoxLayout(left_panel_widget)
        left_panel_layout.setContentsMargins(50, 50, 50, 30)  # Adjust top margin for alignment
        left_panel_layout.setSpacing(20)

        # Expiration Message
        expiration_message = QLabel("Your License\nhave been Expired!")
        expiration_message.setFont(QFont("Poppins", 24, QFont.Bold))
        expiration_message.setStyleSheet(STYLE_SHEET["title"])
        expiration_message.setAlignment(Qt.AlignCenter)
        left_panel_layout.addWidget(expiration_message)

        # Lock Image
        lock_image_path = os.path.join(assets_dir, "Lock_renewal.svg")
        lock_image_label = QLabel()
        lock_image_label.setPixmap(
            QPixmap(lock_image_path).scaled(
                300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        lock_image_label.setAlignment(Qt.AlignCenter)
        lock_image_label.setStyleSheet("background: transparent;")
        left_panel_layout.addWidget(lock_image_label, alignment=Qt.AlignCenter)

        spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        left_panel_layout.addSpacerItem(spacer)

        # Renew Button
        renew_button = QLabel()
        renew_button.setText("<div style='background-color:#21B194; color:#FFFFFF; font-size:20px; font-family:Poppins; font-weight:bold; padding:15px; border-radius:20px; text-align:center; cursor:pointer; width:400px;'>Renew</div>")
        renew_button.setAlignment(Qt.AlignCenter)
        renew_button.setStyleSheet("background: transparent;")
        left_panel_layout.addWidget(renew_button)

        # Add the left panel to the container layout
        container_layout.addWidget(left_panel_widget)

        # Right Panel
        right_panel_widget = QWidget()
        right_panel_widget.setFixedSize(450, 700)  # Fixed size for the right panel
        right_panel_widget.setStyleSheet(STYLE_SHEET["right_panel"])

        # Layout for the right panel
        right_panel_layout = QVBoxLayout(right_panel_widget)
        right_panel_layout.setContentsMargins(0, 100, 0, 30)  # Increase top margin to move content down
        right_panel_layout.setSpacing(50)  # Adjust spacing between elements

        # Image 1 - Centered in the panel
        license_panel_image_path = os.path.join(assets_dir, "license_panel.png")
        image1_label = QLabel()
        image1_label.setPixmap(
            QPixmap(license_panel_image_path).scaled(
                450, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        image1_label.setAlignment(Qt.AlignCenter)
        image1_label.setStyleSheet("background: transparent;")
        right_panel_layout.addWidget(image1_label, alignment=Qt.AlignCenter)

        # Spacer to ensure proper alignment
        spacer = QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Expanding)
        right_panel_layout.addSpacerItem(spacer)

        # Logo (Image 2) - Positioned slightly upward
        logo_image_path = os.path.join(assets_dir, "licensepanelettiksoft.png")
        logo_label = QLabel()
        logo_label.setPixmap(
            QPixmap(logo_image_path).scaled(
                200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background: transparent;")
        right_panel_layout.addWidget(logo_label, alignment=Qt.AlignBottom)

        # Add the right panel to the container layout
        container_layout.addWidget(right_panel_widget)

        # Add the container widget to the outer layout
        outer_layout.addWidget(container_widget, alignment=Qt.AlignCenter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LicenseRenewalPanel()
    window.show()
    sys.exit(app.exec_())
