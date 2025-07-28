
from PyQt5.QtGui import QFont

Module_bg = '#FFFFFF'
Module_border_fg = '#E3E5EC'
Module_active_fg = '#12BCBB'
Module_inactive_fg = '#607182'
Module_width = '80px'
Module_border_size = '2px'
Module_font_family = 'Poppins'
Module_font_size = '14px'
Module_toottip_font_size = 10
Module_font_color = 'white'
Module_tooltip_font_color = 'black'

main_module_style = f"""
                        background-color: {Module_bg}; 
                        width: {Module_width}; 
                        border: none; 
                        border-right: {Module_border_size} 
                        solid {Module_border_fg};
                        font-family: {Module_font_family};
                        font-size: {Module_font_size};
                        color: {Module_font_color};
                    """

main_module_tooltip_style = QFont(Module_font_family, Module_toottip_font_size)

main_module_active_style = f""" 
                                QToolTip {{
                                    color: {Module_tooltip_font_color};
                                }}
                                QPushButton {{
                                    border: none;
                                    border-left: 6px solid {Module_active_fg};
                                }}
                            """

main_module_inactive_style = f""" 
                                QToolTip {{
                                    color: {Module_tooltip_font_color};
                                }}
                                QPushButton {{
                                    border: none;
                                }}
                            """
spacer_style = f""" background-color: transparent; 
                        border: none; 
                    """