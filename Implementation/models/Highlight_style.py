

from PyQt5.QtGui import QFont
import models.Parameters as P

# Attack Leaves Highlights
attakleaves_toolbar_style = f"background-color: {P.ToolBox_bg}; padding: 5px;"
attakleaves_leaf_combobox_style = f"""QComboBox{{background-color: transparent; border:none; font-weight: bold;}}QComboBox::drop-down {{ background-color: transparent; width: 10px; border: none; }} QComboBox::down-arrow {{  width: 0px; image: none; }}"""

attackpaths_gate_style = """
                QPushButton {
                background-color: rgba(0, 0, 0, 0);  /* Transparent background */
                border: none;  /* No border */
                color: black;  /* Text color */
                font-family: 'Roboto';  /* Set font to Roboto */
                font-weight: bold;  /* Bold text */
                font-size: 16px;  /* Font size 10 */
                }
                QPushButton:hover {
                background-color: #D6F8F8;  /* Optional hover color */
                }
        """



