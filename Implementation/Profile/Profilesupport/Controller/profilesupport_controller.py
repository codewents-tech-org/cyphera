from datetime import datetime
from PyQt5.QtWidgets import QApplication, QPushButton, QTextEdit
from Profile.Profilesupport.views.profile_support import ProfileSupport

class ProfileSupportController:
    def __init__(self):
        self.view = ProfileSupport()
        self.connect_signals()

    def connect_signals(self):
        # Connect the Submit button signal to handle_submit
        self.view.submit_button.clicked.connect(self.handle_submit)

    def handle_submit(self):
        # Get the typed message from the input box
        typed_message = self.view.message_input.toPlainText().strip()

        if typed_message:
            # Get the current timestamp
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Format the message with timestamp
            formatted_message = f"{timestamp}\n{typed_message}\n"

            # Append the formatted message to the tickets box
            self.view.tickets_box.append(formatted_message)

            # Clear the message input box after submission
            self.view.message_input.clear()

    def start(self):
        # Show the main view
        self.view.show()
