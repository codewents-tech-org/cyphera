
from PyQt5.QtGui import QFont

SubModule_bg = '#FFFFFF'
SubModule_border_fg = '#E3E5EC'
SubModule_width = '120px'
SubModule_border_size = '2px'
SubModule_font_family = 'Poppins'
SubModule_font_size = '14px'
SubModule_label_font_size = '18px'
SubModule_font_size_int = 14
SubModule_font_color = '#41484F'
SubModule_hover_bg = '#D6F8F8'
SubModule_active_bg = '#D6F8F8'
SubModule_inactive_bg = SubModule_bg
SubModule_active_font_color = '#009D9C'
SubModule_inactive_font_color = '#41484F'



sub_module_style = f""" background-color: {SubModule_bg}; 
                        width: {SubModule_width}; 
                        border: none; 
                        border-right: {SubModule_border_size} solid {SubModule_border_fg};
                    """

sub_module_text_style = QFont(SubModule_font_family, SubModule_font_size_int)

sub_module_active_style = f""" 
                                QPushButton {{
                                    background-color: {SubModule_active_bg};
                                    font-family: {SubModule_font_family};
                                    font-size: {SubModule_font_size};
                                    color: {SubModule_active_font_color};
                                    border: none;
                                    text-align: left;
                                    padding-left: 20px;
                                    border-top-right-radius: 8px;
                                    border-bottom-right-radius: 8px;
                                }}
                                QPushButton:hover {{
                                    background-color: {SubModule_hover_bg};
                                    text-align: left;
                                    border-top-right-radius: 8px;
                                    border-bottom-right-radius: 8px;
                                }}
                            """

sub_module_inactive_style = f""" 
                                QPushButton {{
                                    background-color: {SubModule_inactive_bg};
                                    font-family: {SubModule_font_family};
                                    font-size: {SubModule_font_size};
                                    color: {SubModule_inactive_font_color};
                                    border: none;
                                    text-align: left; 
                                    padding-left: 20px; 
                                    border-top-right-radius: 8px;
                                    border-bottom-right-radius: 8px;                               
                                }}
                                QPushButton:hover {{
                                    background-color: {SubModule_hover_bg};
                                    text-align: left;
                                    border-top-right-radius: 8px;
                                    border-bottom-right-radius: 8px;
                                }}
                            """

sub_module_label_style = f"""
                            QLabel {{
                                font-size: {SubModule_label_font_size};
                                font-family: {SubModule_font_family};
                                font-weight: bold;
                                color: {SubModule_inactive_font_color};
                                background-color: {SubModule_bg};
                                border: none;
                                border-bottom: {SubModule_border_size} solid {SubModule_border_fg};
                                text-align: centre;
                                padding-bottom: 10px;
                                padding-left: 20px;
                            }}
                        """