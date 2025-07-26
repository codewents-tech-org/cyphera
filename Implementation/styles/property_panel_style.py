
property_bg = '#FFFFFF'
property_font_family = 'poppins'
property_font_size = '14px'
property_heading_label_font_size = '20px'
property_label_font_size = '14px'
property_input_font_size = '14px'
property_group_label_font_size = '12px'
property_font_color = '#41484F'
property_label_font_color = '#41484F'
property_border_size = '2px'
property_border_fg = '#E3E5EC'
property_save_button_bg = '#17CFCE'

switch_property_panel_style = f"""
                        background-color: {property_bg};
                        border: none; 
                        border-left: {property_border_size} solid {property_border_fg}; 
                        font-family: {property_font_family};
                        font-size: {property_font_size};
                        color: {property_font_color};
                    """
switch_button_style = f"""border: transparent; """

property_panel_style = f"""
                        background-color: {property_bg};
                        border: none; 
                        border-right: {property_border_size} solid {property_border_fg}; 
                        font-family: {property_font_family};
                        font-size: {property_font_size};
                        color: {property_font_color};
                    """


Scroll_area_style = f"""
                    QScrollBar:vertical {{ 
                        border: none; 
                        background: #f0f0f0;  
                        width: 10px; 
                        margin: 0px 0px 0px 0px; 
                    }}
                    QScrollBar::handle:vertical {{ 
                        background: #c1c1c1; 
                        min-height: 0px; 
                        border-radius: 5px; 
                    }}
                    QScrollBar::add-line:vertical,
                    QScrollBar::sub-line:vertical {{ 
                        height: 0px; 
                        subcontrol-origin: margin; 
                    }}
                    QScrollBar::add-page:vertical, 
                    QScrollBar::sub-page:vertical {{ 
                        background: none; 
                    }}
                    QScrollBar:horizontal {{ 
                        border: none; 
                        background: #f0f0f0; 
                        height: 10px; 
                        margin: 0px 0px 0px 0px; 
                    }}
                    QScrollBar::handle:horizontal {{ 
                        background: #c1c1c1; 
                        min-width: 0px; 
                        border-radius: 5px; 
                    }}
                    QScrollBar::add-line:horizontal,
                    QScrollBar::sub-line:horizontal {{ 
                        width: 0px; 
                        subcontrol-origin: margin; 
                    }}
                    QScrollBar::add-page:horizontal, 
                    QScrollBar::sub-page:horizontal {{ 
                        background: none;  
                    }}
                """


property_heading_label_style = f"""
                            QLabel {{
                                font-size: {property_heading_label_font_size};
                                font-family: {property_font_family};
                                font-weight: bold;
                                color: {property_label_font_color};
                                background-color: transparent;
                                border: none solid transparent;
                                text-align: left;
                                padding-bottom: 5px;
                            }}
                        """

property_label_style = f"""
                            QLabel {{
                                font-size: {property_label_font_size};
                                font-family: {property_font_family};
                                color: {property_label_font_color};
                                background-color: transparent;
                                border: none;
                                text-align: left;
                                padding-left: 5px;
                                font-weight: bold;
                            }}
                        """

property_singleline_input_style = f"""
                            QLineEdit {{
                                font-size: {property_label_font_size};
                                font-family: {property_font_family};
                                color: {property_label_font_color};
                                background-color: transparent;
                                border-left:{property_border_size} solid {property_border_fg};
                                border-right:{property_border_size} solid {property_border_fg};
                                border-top:{property_border_size} solid {property_border_fg};
                                border-bottom:{property_border_size} solid {property_border_fg};
                                text-align: left;
                                padding-left: 5px;
                                border-radius: 8px;
                            }}
                        """

property_multiline_input_style = f"""
                            QTextEdit {{
                                font-size: {property_label_font_size};
                                font-family: {property_font_family};
                                color: {property_label_font_color};
                                background-color: transparent;
                                border-left:{property_border_size} solid {property_border_fg};
                                border-right:{property_border_size} solid {property_border_fg};
                                border-top:{property_border_size} solid {property_border_fg};
                                border-bottom:{property_border_size} solid {property_border_fg};
                                text-align: left;
                                padding-left: 5px;
                                border-radius: 8px;
                            }}
                        """

property_spacer_style = f""" background-color: transparent; 
                        border: none; 
                    """

property_save_button_style = f"""
                                background-color: {property_save_button_bg};
                                border: 1px solid {property_border_fg};
                                border-radius: 8px; 
                                padding: 5px;
                            """

property_combobox_style = f"""
                    QComboBox {{ 
                        font-size: {property_font_size}; 
                        font-family: {property_font_family};
                        color: {property_font_color};
                        background-color: transparent;
                        border-left:{property_border_size} solid {property_border_fg};
                        border-right:{property_border_size} solid {property_border_fg};
                        border-top:{property_border_size} solid {property_border_fg};
                        border-bottom:{property_border_size} solid {property_border_fg};
                        text-align: left;
                        padding-left: 5px;
                        border-radius: 8px;
                        }} 
                    QComboBox::drop-down {{ 
                        width: 0px; 
                        border: none; }} 
                    QComboBox::down-arrow {{ 
                        width: 0px; 
                        image: none; }} 
                    QComboBox:hover {{ 
                        background-color: transparent; 
                        color: {property_font_color}; 
                    }} 
                    QComboBox QAbstractItemView {{ 
                        color: {property_font_color}; /* Set the default text color of items */
                        background-color: {property_bg}; /* Set background for the item list */
                    }}
                    QComboBox QAbstractItemView::item:hover {{ 
                        color: {property_font_color}; /* Set text color when hovering */
                        background-color:{property_save_button_bg}; /* Optional: background color of hovered items */
                    }}
                    QComboBox QAbstractItemView::item:selected {{ 
                        color: {property_font_color}; /* Set text color for selected items */
                        background-color: {property_save_button_bg}; /* Optional: background color for selected items */
                    }}
                    QComboBox QAbstractItemView::item:QToolTip {{ 
                        color: {property_font_color}; /* Set text color when hovering */
                        background-color: transparent; /* Optional: background color of hovered items */
                    }}
                    QComboBox:QToolTip {{
                        color: {property_font_color}; /* Set tooltip text color to black */
                        background-color: transparent; /* Set tooltip background color */
                        border: 1px solid {property_border_fg}; /* Optional: border for the tooltip */
                    }} """

property_line_style = f"""
                            background-color: {property_font_color}
                        """

property_group_label_style = f"""
                            QLabel {{
                                font-size: {property_group_label_font_size};
                                font-family: {property_font_family};
                                color: {property_label_font_color};
                                background-color: transparent;
                                border: none;
                                text-align: left;
                                padding-left: 5px;
                                font-weight: bold;
                            }}
                        """