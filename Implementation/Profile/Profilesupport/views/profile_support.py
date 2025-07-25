from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSpacerItem
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import Qt
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from Profile.views.profile_label import Profilelabel


# Add the 'Implementation' folder to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from styles.profile_style import profile_support_styles


class ProfileSupport(QWidget):
    """Profile Support UI displaying support and tickets."""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Main layout for the entire UI
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)  # Margins for the main layout
        main_layout.setSpacing(20)

        # Add the Ettiksoft profile section at the top
        profile_label = Profilelabel()  # Use the existing ProfileLabel class
        main_layout.addWidget(profile_label)

        # Add the Support and Tickets sections
        support_box = self.create_support_box()
        tickets_box = self.create_tickets_box()

        main_layout.addWidget(support_box)
        main_layout.addWidget(tickets_box)

        # Add stretch to ensure the content stays at the top
        main_layout.addStretch()

    def create_support_box(self):
        """Create a box for support input fields."""
        outer_box_layout = QVBoxLayout()
        outer_box_layout.setContentsMargins(10, 10, 10, 10)
        outer_box_layout.setSpacing(15)

        # Title label
        title_label = QLabel("Support")
        title_label.setFont(QFont("Poppins", 14, QFont.Bold))
        title_label.setStyleSheet(profile_support_styles["title_label"])
        outer_box_layout.addWidget(title_label)

        # Email and Phone layout
        email_phone_layout = QHBoxLayout()

        # Email layout
        email_layout = QVBoxLayout()
        email_label = QLabel("Email")
        email_label.setFont(QFont("Poppins", 10))
        email_label.setStyleSheet(profile_support_styles["subtitle_label"])
        self.email_input = QLineEdit()
        self.email_input.setFont(QFont("Poppins", 11))
        self.email_input.setStyleSheet(profile_support_styles["input_field"])
        self.email_input.setPlaceholderText("Enter your email")
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)

        email_phone_layout.addLayout(email_layout)

        # Spacer between email and phone
        spacer = QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        email_phone_layout.addSpacerItem(spacer)

        # Phone layout
        phone_layout = QVBoxLayout()
        phone_label = QLabel("Phone")
        phone_label.setFont(QFont("Poppins", 10))
        phone_label.setStyleSheet(profile_support_styles["subtitle_label"])
        self.phone_input = QLineEdit()
        self.phone_input.setFont(QFont("Poppins", 11))
        self.phone_input.setStyleSheet(profile_support_styles["input_field"])
        self.phone_input.setPlaceholderText("Enter your phone")
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)

        email_phone_layout.addLayout(phone_layout)

        # Add email and phone layout to the outer layout
        outer_box_layout.addLayout(email_phone_layout)

        # Message box
        message_label = QLabel("Message")
        message_label.setFont(QFont("Poppins", 10))
        message_label.setStyleSheet(profile_support_styles["subtitle_label"])
        self.message_input = QTextEdit()
        self.message_input.setFont(QFont("Poppins", 11))
        self.message_input.setStyleSheet(profile_support_styles["message_box"])
        self.message_input.setPlaceholderText("Type your issue or message and click submit.")
        outer_box_layout.addWidget(message_label)
        outer_box_layout.addWidget(self.message_input)

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setFont(QFont("Poppins", 11, QFont.Bold))
        self.submit_button.setStyleSheet(profile_support_styles["button"])
        self.submit_button.clicked.connect(self.submit_message)
        outer_box_layout.addWidget(self.submit_button, alignment=Qt.AlignLeft)

        # Wrap layout in a frame
        outer_box = QFrame()
        outer_box.setLayout(outer_box_layout)
        outer_box.setStyleSheet(profile_support_styles["frame"])

        return outer_box

    def create_tickets_box(self):
        """Create a box for tickets display."""
        outer_box_layout = QVBoxLayout()
        outer_box_layout.setContentsMargins(10, 10, 10, 10)
        outer_box_layout.setSpacing(15)

        # Title label
        title_label = QLabel("Tickets")
        title_label.setFont(QFont("Poppins", 14, QFont.Bold))
        title_label.setStyleSheet(profile_support_styles["title_label"])
        outer_box_layout.addWidget(title_label)

        # Tickets box
        self.tickets_box = QTextEdit()
        self.tickets_box.setFont(QFont("Poppins", 11))
        self.tickets_box.setStyleSheet(profile_support_styles["tickets_box"])
        self.tickets_box.setReadOnly(True)
        outer_box_layout.addWidget(self.tickets_box)

        # Wrap layout in a frame
        outer_box = QFrame()
        outer_box.setLayout(outer_box_layout)
        outer_box.setStyleSheet(profile_support_styles["frame"])

        return outer_box

    def submit_message(self):
        """Handle message submission."""
        typed_message = self.message_input.toPlainText().strip()
        if typed_message:
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            formatted_message = f"<span style='color: #888888;'>{timestamp}</span> - <span style='color: black;'>{typed_message}</span>"
            existing_messages = self.tickets_box.toHtml()
            updated_messages = f"{formatted_message}<br>{existing_messages}"
            self.tickets_box.setHtml(updated_messages)
            self.message_input.clear()

    def load_data(self): pass

# Main function to run the app
def main():
    app = QApplication([])
    window = ProfileSupport()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
