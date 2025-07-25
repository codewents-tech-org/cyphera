import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
import os

# Add the 'Implementation' folder to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))



from Profile.Profilebillingdetails.Controller import billingdetails_controller  # Corrected import for the control module
from Profile.views.profile_label import Profilelabel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from styles.profile_style import profile_billing_styles


class ProfileBilling(QWidget):
    """Profile Billing UI displaying profile, billing details, and plan details."""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Main layout for the entire UI
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)  # Margins for the main layout
        main_layout.setSpacing(20)

        # Add the ProfileLabel at the top
        profile_label = Profilelabel()  # Use the existing ProfileLabel class
        main_layout.addWidget(profile_label)

        # Create outer frame for Billing Details
        billing_details_box = self.create_outer_box(
            billingdetails_controller.billing_details_answers,
            billingdetails_controller.billing_details_title,
        )

        # Create outer frame for Plan Details
        plan_details_box = self.create_outer_box(
            billingdetails_controller.plan_details_answers,
            billingdetails_controller.plan_details_title,
        )

        # Add the outer boxes to the main layout
        main_layout.addWidget(billing_details_box)
        main_layout.addWidget(plan_details_box)

        # Add stretch to ensure the content stays at the top
        main_layout.addStretch()

    def create_outer_box(self, answers, title):
        """Create an outer box with two columns of labels and answers."""
        # Create outer box frame
        outer_box_layout = QVBoxLayout()
        outer_box_layout.setContentsMargins(10, 10, 10, 10)  # Margins for the content inside the box
        outer_box_layout.setSpacing(1)

        # Create title label (centered and styled)
        title_label = QLabel(title)
        title_label.setFont(QFont("Poppins", 14, QFont.Bold))  # Font size for title
        title_label.setStyleSheet(profile_billing_styles["title_label"])  # Apply stylesheet
        title_label.setAlignment(Qt.AlignLeft)  # Align title to the left
        title_label.setContentsMargins(10, 10, 10, 10)  # Adjust spacing
        outer_box_layout.addWidget(title_label)

        # Create a layout to display the labels and values (two columns)
        details_layout = QHBoxLayout()

        # Create left column for the labels and answers
        left_column_layout = QVBoxLayout()

        # Create right column for the labels and answers
        right_column_layout = QVBoxLayout()

        # Loop through the fields (label, value) pairs and split between left and right columns
        labels = list(answers.keys())
        for i, label in enumerate(labels):
            value = answers[label]

            # Create label widget for the field
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Poppins", 10))  # Font size for field labels
            label_widget.setStyleSheet(profile_billing_styles["label_widget"])  # Apply stylesheet
            label_widget.setAlignment(Qt.AlignLeft)  # Align field label to the left

            # Create a non-editable QLineEdit widget for the answer
            value_widget = QLineEdit(value)
            value_widget.setFont(QFont("Poppins", 11))  # Font size slightly larger for answers
            value_widget.setStyleSheet(profile_billing_styles["value_widget"])  # Apply stylesheet
            value_widget.setReadOnly(True)  # Make it non-editable
            value_widget.setAlignment(Qt.AlignLeft)  # Align answer to the left

            # Add the label and value to the respective columns
            if i % 2 == 0:  # Even index to left column
                left_column_layout.addWidget(label_widget)
                left_column_layout.addWidget(value_widget)
            else:  # Odd index to right column
                right_column_layout.addWidget(label_widget)
                right_column_layout.addWidget(value_widget)

        # Add the left and right columns to the details layout
        details_layout.addLayout(left_column_layout)
        details_layout.addLayout(right_column_layout)

        # Add the details layout to the outer box
        outer_box_layout.addLayout(details_layout)

        # Wrap the outer box layout in a frame for styling
        outer_box = QFrame()
        outer_box.setLayout(outer_box_layout)
        outer_box.setStyleSheet(profile_billing_styles["outer_box"])  # Apply stylesheet

        return outer_box

    def load_data(self): pass

# Main function to run the app
def main():
    app = QApplication([])
    window = ProfileBilling()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
