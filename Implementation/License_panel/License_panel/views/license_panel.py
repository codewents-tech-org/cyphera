from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import sys
import os
import constants

# Adjust sys.path to include the Implementation directory
current_dir = os.path.dirname(os.path.abspath(__file__))
implementation_dir = os.path.abspath(os.path.join(current_dir, '../../../'))
if implementation_dir not in sys.path:
    sys.path.insert(0, implementation_dir)

# Import styles
from styles.license_panel_style import (
   STYLE_SHEET
)
assets_dir = os.path.join(current_dir, "../../../../Implementation/assets/images/")

class LicensePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(STYLE_SHEET["main"])
        self.org_placeholder = ""
        self.plan_placeholder = ""
        self.ip_placeholder = ""
        self.expiry_placeholder = ""
        self.initUI()

    def update_user_data(self):
        print("Updating user data...")
        user_data = constants.personal_data

        # Assign new values
        self.org_placeholder = user_data["org_detail"]["Name"]
        self.plan_placeholder = user_data["billing_detail"]["Plan Name"]
        self.ip_placeholder = user_data["org_detail"]["IP Address"]
        self.expiry_placeholder = user_data["billing_detail"]["Expiry Date"]

        # Update the UI fields with the new values
        self.hidden_inputs[0].setText(self.org_placeholder)
        self.hidden_inputs[1].setText(self.plan_placeholder)
        self.hidden_inputs[2].setText(self.ip_placeholder)
        self.hidden_inputs[3].setText(self.expiry_placeholder)

        # Make sure labels and fields are visible
        for label, input_field in zip(self.hidden_labels, self.hidden_inputs):
            label.setVisible(True)
            input_field.setVisible(True)

        print("User data updated successfully!")

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
        left_panel_layout = QVBoxLayout(left_panel_widget)
        left_panel_layout.setContentsMargins(30, 30, 30, 30)
        left_panel_layout.setSpacing(15)

        # Title
        title = QLabel("Activate License")
        title.setFont(QFont("Poppins", 24, QFont.Bold))
        title.setStyleSheet(STYLE_SHEET["title"])
        left_panel_layout.addWidget(title)

        # Description
        description = QLabel(
            "The Automotive Security Management System TARA (Threat Analysis and Risk Assessment) identifies, "
            "evaluates, and mitigates cybersecurity risks in automotive systems.\n"
            "It ensures compliance with industry standards like ISO/SAE 21434 and UNECE WP.29 regulations."
        )
        description.setWordWrap(True)
        description.setFont(QFont("Poppins", 10))
        description.setStyleSheet(STYLE_SHEET["description"])
        left_panel_layout.addWidget(description)

        # License Key Field and Validate Button
        license_layout = QVBoxLayout()

        self.license_key_field = QLineEdit()
        self.license_key_field.setFixedSize(700, 40)
        self.license_key_field.setFont(QFont("Poppins", 10))
        self.license_key_field.setPlaceholderText("Enter License Key")
        self.license_key_field.setStyleSheet(STYLE_SHEET["line_edit"])
        license_layout.addWidget(self.license_key_field, alignment=Qt.AlignLeft)

        self.error_label = QLabel("")  # Error message label
        self.error_label.setFont(QFont("Poppins", 10))
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setVisible(False)  # Initially hidden
        license_layout.addWidget(self.error_label, alignment=Qt.AlignLeft)

        self.validate_button = QPushButton("Validate")
        self.validate_button.setFixedSize(120, 40)
        self.validate_button.setFont(QFont("Poppins", 10, QFont.Bold))
        self.validate_button.setStyleSheet(STYLE_SHEET["button_default"])
        license_layout.addWidget(self.validate_button)

        left_panel_layout.addLayout(license_layout)

        # Widgets: Progress Bar and Organization Details
        self.progress_label = QLabel("License Activated")
        self.progress_label.setFont(QFont("Poppins", 10))
        self.progress_label.setStyleSheet(STYLE_SHEET["description"])
        left_panel_layout.addWidget(self.progress_label, alignment=Qt.AlignLeft)
        self.progress_label.setVisible(False)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(15)  # Thinner progress bar
        self.progress_bar.setStyleSheet(STYLE_SHEET["progress_bar"])
        left_panel_layout.addWidget(self.progress_bar)
        self.progress_bar.setVisible(False)

        self.org_details_layout = self.update_org_details_layout()
        left_panel_layout.addLayout(self.org_details_layout)

        # Add spacer to preserve layout
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        left_panel_layout.addSpacerItem(spacer)

        # Proceed Button
        self.proceed_button = QPushButton("Proceed")
        self.proceed_button.setFixedSize(180, 40)
        self.proceed_button.setFont(QFont("Poppins", 12, QFont.Bold))
        self.proceed_button.setStyleSheet(STYLE_SHEET["proceed_button"])
        self.proceed_button.setVisible(False)
        # Connect Proceed button to navigation function
        self.proceed_button.clicked.connect(self.navigate_to_dashboard)

        left_panel_layout.addWidget(self.proceed_button, alignment=Qt.AlignCenter)

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
        image1_path = os.path.join(assets_dir, "license_panel.png")
        image1_label = QLabel()
        image1_label.setPixmap(
            QPixmap(image1_path).scaled(
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
        logo_path = os.path.join(assets_dir, "licensepanelettiksoft.png")
        logo_label = QLabel()
        logo_label.setPixmap(
            QPixmap(logo_path).scaled(
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

    def update_org_details_layout(self):
        self.org_details_layout = QGridLayout()
        self.org_details_layout.setSpacing(15)

        labels = ["Organisation", "Plan", "IP", "Expires On"]
        placeholders = [
            self.org_placeholder,
            self.plan_placeholder,
            self.ip_placeholder,
            self.expiry_placeholder,
        ]

        self.hidden_labels = []
        self.hidden_inputs = []

        for i, (label_text, placeholder_text) in enumerate(zip(labels, placeholders)):
            label = QLabel(label_text)
            label.setFont(QFont("Poppins", 10))
            label.setStyleSheet(STYLE_SHEET["description"])
            row, col = divmod(i, 2)
            self.org_details_layout.addWidget(label, row * 2, col, alignment=Qt.AlignLeft)
            label.setVisible(False)
            self.hidden_labels.append(label)

            value = QLineEdit()
            value.setFont(QFont("Poppins", 10))
            value.setReadOnly(True)
            value.setPlaceholderText(placeholder_text)
            value.setFixedSize(330, 35)  # Adjusted width for alignment
            value.setStyleSheet(STYLE_SHEET["input_field"])
            self.org_details_layout.addWidget(value, row * 2 + 1, col, alignment=Qt.AlignLeft)
            value.setVisible(False)
            self.hidden_inputs.append(value)
        return self.org_details_layout

    def navigate_to_dashboard(self):
        print("Proceed button clicked! Navigating...")

        print("Opening Home Panel...")
        from views.TARA_Tool import Application  # Import here to ensure it's loaded after the splash
        main_window = Application()
        main_window.show()

        # Hide the current window if needed
        self.parent().close()  # If `LicensePanel` is inside `QMainWindow`, close it


