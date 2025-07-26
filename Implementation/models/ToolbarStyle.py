
import models.Parameters as P

image_label_style = """QLabel {padding: 5px;}"""

toolbar_style = f"background-color: {P.ToolBox_bg}; padding: 5px;"

label_style = f"""
            font-family: Roboto;
            font-size: 26px; 
            font-weight: bold; 
            color: {P.Black}; 
            padding: 5px; 
            margin-left: 10px;
        """

dropdown_button_style = """
            QToolButton {
                background: transparent;
                border: none;
                margin-top: 10px;
                padding: 5px; 
            }
            QToolButton:hover {
                background: transparent;
                border: none;
            }
        """
button_style = """
            QPushButton {
                border: transparent; 
                background: transparent;
                padding: 5px;
            }
            QPushButton:hover {
                background: lightgray;
            }
            QToolTip {
                background-color: #f0f0f0;
                color: #000;
                border: 1px solid black;
            }          
            QPushButton:clicked {
                background-color: blue;
                border: 2px solid blue;
            }
        """