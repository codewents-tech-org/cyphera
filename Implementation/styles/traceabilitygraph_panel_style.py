from PyQt5.QtGui import(QFont)

action_bg = '#FCFCFC'
action_font_family = 'poppins'
action_font_size = '16px'
action_font_color = 'black'
action_border_size = '2px'
action_border_fg = '#E3E5EC'

trace_panel_style = f"""
                        QScrollArea {{
                            background-color: {action_bg};
                            border: 2px solid {action_border_fg};
                            border-bottom-left-radius: 10px;
                            border-bottom-right-radius: 10px;
                        }}
                        QScrollArea QScrollBar:vertical {{ 
                            border: none; 
                            background: #f0f0f0;  
                            width: 10px; 
                            margin: 0px 0px 0px 0px; 
                        }}
                        QScrollArea QScrollBar::handle:vertical {{ 
                            background: #c1c1c1; 
                            min-height: 0px; 
                            border-radius: 5px; 
                        }}
                        QScrollArea QScrollBar::add-line:vertical,
                        QScrollArea QScrollBar::sub-line:vertical {{ 
                            height: 0px; 
                            subcontrol-origin: margin; 
                        }}
                        QScrollArea QScrollBar::add-page:vertical, 
                        QScrollArea QScrollBar::sub-page:vertical {{ 
                            background: none; 
                        }}
                        QScrollArea QScrollBar:horizontal {{ 
                            border: none; 
                            background: #f0f0f0; 
                            height: 10px; 
                            margin: 0px 0px 0px 0px; 
                        }}
                        QScrollArea QScrollBar::handle:horizontal {{ 
                            background: #c1c1c1; 
                            min-width: 0px; 
                            border-radius: 5px; 
                        }}
                        QScrollArea QScrollBar::add-line:horizontal,
                        QScrollArea QScrollBar::sub-line:horizontal {{ 
                            width: 0px; 
                            subcontrol-origin: margin; 
                        }}
                        QScrollArea QScrollBar::add-page:horizontal, 
                        QScrollArea QScrollBar::sub-page:horizontal {{ 
                            background: none;  
                        }}
                    """
trace_header_panel_style = f"""
                            background-color: #FFFFFF;
                            border: 2px solid {action_border_fg};
                            color: #41484F;
                            border-top-left-radius: 10px;
                            border-top-right-radius: 10px;
                        """

# Traceability Graph Highlights
traceabilitygraph_label_style = f"""border-bottom: 3px solid #CCD2E3; color: #41484F"""
traceabilitygraph_label_font = QFont("Poppins", 20, QFont.Bold)
traceabilitygraph_box_style = f"border: 1px solid #CCD2E3; background-color: #FFFFFF; color: #41484F; border-radius: 10px"
traceabilitygraph_box_font = QFont("Poppins", 12)
# traceabilitygraph_selected_box_style = f"border: 2px solid #17CFCE; background-color: #D6F8F8; border-left: 10px solid #17CFCE; color: #41484F"
traceabilitygraph_selected_box_style = f"border: 2px solid #17CFCE; background-color: #D6F8F8; border-left: 10px solid #17CFCE; color: #41484F; border-radius: 10px 10px 10px 0px; border-top-left-radius: 3px; border-bottom-left-radius: 3px"
