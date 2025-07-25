import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from styles.profile_style import profile_styles



class Profilelabel(QWidget):
    """Profile UI for displaying Ettiksoft details only."""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Main layout for the entire UI
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Removed margins for the main layout
        main_layout.setSpacing(0)  # Removed spacing for the main layout

        # Add the Ettiksoft section directly to the main layout
        ettiksoft_section = self.create_outer_box()
        main_layout.addWidget(ettiksoft_section)

    def create_outer_box(self):
        """Create an outer box containing the profile content."""
        # Create the outer box frame
        outer_box = QFrame()
        outer_box_layout = QHBoxLayout(outer_box)
        outer_box_layout.setContentsMargins(10, 10, 10, 10)  # Add some margins for the content inside the box
        outer_box_layout.setSpacing(15)  # Add space between the icon and text

        # Add a circular icon to the left
        icon_label = QLabel()
        icon_label.setFixedSize(90, 90)  # Icon size
        icon_label.setStyleSheet(profile_styles["icon_label"])  # Apply style for the icon
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setText("E")  # Icon text

        # Add a vertical layout for the title and details
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(5, 5, 5, 5)  # Add slight padding inside the text layout
        text_layout.setSpacing(5)  # Reduce the spacing between the lines

        # Add the title with Poppins font
        title_label = QLabel("ETTIKSOFT TECHNOLOGIES")
        title_label.setFont(QFont("Poppins", 12, QFont.Bold))
        title_label.setStyleSheet(profile_styles["title_label"])  # Apply style for the title
        text_layout.addWidget(title_label)

        # Add the details
        details_label = QLabel("Ettiksoft Technologies Private Ltd")
        details_label.setFont(QFont("Poppins", 10))
        details_label.setStyleSheet(profile_styles["details_label"])  # Apply style for details
        text_layout.addWidget(details_label)

        location_label = QLabel("Namakkal, Tamil Nadu")
        location_label.setFont(QFont("Poppins", 10))
        location_label.setStyleSheet(profile_styles["details_label"])  # Apply style for location
        text_layout.addWidget(location_label)

        # Add the logo and text layout to the box layout
        outer_box_layout.addWidget(icon_label)
        outer_box_layout.addLayout(text_layout)

        # Set the style for the outer box
        outer_box.setStyleSheet(profile_styles["outer_box"])  # Apply style for the outer box

        return outer_box


# Main function to run the app
def main():
    app = QApplication([])
    window = Profilelabel()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
