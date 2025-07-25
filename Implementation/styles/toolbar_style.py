from PyQt5.QtGui import QFont

toolbar_bg = "#FFFFFF"
toolbar_border_fg = "#E3E5EC"
toolbar_height = "49px"
toolbar_button_height = "30px"
toolbar_border_size = "2px"
toolbar_font_family = "Poppins"
toolbar_font_size = "14px"
toolbar_label_font_size = "18px"
toolbar_font_size_int = 14
toolbar_font_color = "black"
toolbar_label_font_color = "#41484F"
toolbar_label_width = "250px"
toolbar_button_bg = "#F6F7FB"
toolbar_hover_bg = "#17CFCE"


toolbar_style = f""" background-color: {toolbar_bg}; 
                        height: {toolbar_height}; 
                        border: none; 
                        color: {toolbar_font_color};
                        border-bottom: {toolbar_border_size} solid {toolbar_border_fg};
                    """

toolbar_text_style = QFont(toolbar_font_family, toolbar_font_size_int)

toolbar_label_style = f"""
                            QLabel {{
                                font-size: {toolbar_label_font_size};
                                font-family: {toolbar_font_family};
                                font-weight: bold;
                                color: {toolbar_label_font_color};
                                background-color: transparent;
                                border: none solid transparent;
                                width: {toolbar_label_width};
                                text-align: left;
                                padding-left: 5px;
                            }}
                        """

toolbar_arrow_style = f""" background-color: transparent; 
                        border: none; 
                    """
toolbar_spacer_style = f""" background-color: transparent; 
                        border: none; 
                    """
toolbar_button_style = f"""
                        QToolButton {{
                            border: {toolbar_border_size} solid {toolbar_border_fg};
                            color: {toolbar_label_font_color};
                            font-size: {toolbar_font_size};
                            font-family: {toolbar_font_family};
                            font-weight: bold;
                            height: {toolbar_button_height};
                            background-color: {toolbar_button_bg};
                            border-radius: 8px;
                        }}
                        QToolButton:hover {{
                            background-color: {toolbar_hover_bg};
                        }}
                        QToolButton:checked {{
                            background-color: {toolbar_hover_bg};
                        }}
                        """

toolbar_button_hover_style = f"""
                        QToolButton {{
                            border: {toolbar_border_size} solid {toolbar_border_fg};
                            color: {toolbar_label_font_color};
                            font-size: {toolbar_font_size};
                            font-family: {toolbar_font_family};
                            font-weight: bold;
                            height: {toolbar_button_height};
                            background-color: {toolbar_hover_bg};
                            border-radius: 8px;
                        }}
                        """

toolbar_combobox_style = f"""
                            QComboBox {{
                                background-color: #FFFFFF;
                                border: 2px solid {toolbar_border_fg};
                                font-size: 16px;
                                color: {toolbar_font_color};  /* Text color */
                            }}
                        """
toolbar_dropdown_button_style = f"""
    QToolButton {{
        border: {toolbar_border_size} solid {toolbar_border_fg};
        color: {toolbar_label_font_color};
        font-size: {toolbar_font_size};
        font-family: {toolbar_font_family};
        font-weight: bold;
        height: {toolbar_button_height};
        background-color: {toolbar_button_bg};
        border-radius: 8px;
        padding-right: 6px;
        padding-bottom: 1px;
        vertical-align: middle;
    }}
    QToolButton:hover {{
        background-color: {toolbar_hover_bg};
    }}
    QToolButton:checked {{
        background-color: {toolbar_hover_bg};
    }}
    QToolButton::menu-indicator {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        padding-right: 4px;
        padding-bottom: 1px;
    }}
"""
toolbar_dropdown_menu_style = """
    QMenu {
        background-color: white;
        border: 1px solid #ccc;
    }
"""

toolbar_dropdown_button_inner_style = """
    QPushButton {
        border: none;
        background-color: white;
        padding: 4px;
    }
    QPushButton:hover {
        background-color: #f0f0f0;
    }
"""
