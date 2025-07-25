
action_bg = '#FFFFFF'
action_font_family = 'poppins'
action_font_size = '16px'
action_font_color = 'black'
action_border_size = '2px'
action_border_fg = '#E3E5EC'

action_panel_style = f"""
                        background-color: #EAEAEA;
                        border: 2px solid {action_border_fg}; 
                        font-family: {action_font_family};
                        font-size: {action_font_size};
                        color: {action_font_color};
                        border-radius: 10px;
                    """


tree_style = f"""
                QGraphicsView {{
                    background-color: {action_bg};
                        border: none; 
                        font-family: {action_font_family};
                        font-size: {action_font_size};
                        color: {action_font_color};
                        padding: 20px;
                }}
            QGraphicsView QScrollBar:vertical {{ 
                border: none; 
                background: #f0f0f0;  
                width: 10px; 
                margin: 0px 0px 0px 0px; 
                }}
            QGraphicsView QScrollBar::handle:vertical {{ 
                background: #c1c1c1; 
                min-height: 0px; 
                border-radius: 5px; 
                }}
            QGraphicsView QScrollBar::add-line:vertical,
            QGraphicsView QScrollBar::sub-line:vertical {{ 
                height: 0px; 
                subcontrol-origin: margin; 
                }}
            QGraphicsView QScrollBar::add-page:vertical, 
            QGraphicsView QScrollBar::sub-page:vertical {{ 
                background: none; 
                }}
            QGraphicsView QScrollBar:horizontal {{ 
                border: none; 
                background: #f0f0f0; 
                height: 10px; 
                margin: 0px 0px 0px 0px; 
                }}
            QGraphicsView QScrollBar::handle:horizontal {{ 
                background: #c1c1c1; 
                min-width: 0px; 
                border-radius: 5px; 
                }}
            QGraphicsView QScrollBar::add-line:horizontal,
            QGraphicsView QScrollBar::sub-line:horizontal {{ 
                width: 0px; 
                subcontrol-origin: margin; 
                }}
            QGraphicsView QScrollBar::add-page:horizontal, 
            QGraphicsView QScrollBar::sub-page:horizontal {{ 
                background: none;  
                }}
            """
