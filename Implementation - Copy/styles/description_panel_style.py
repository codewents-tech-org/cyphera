

text_panel_style = f"""
    QTextEdit {{
        background-color: white;
        color: black;
        padding: 20px;
    }}
    QTextEdit QScrollBar:vertical {{ 
        border: none; 
        background: #f0f0f0;  
        width: 10px; 
        margin: 0px 0px 0px 0px; 
    }}
    QTextEdit QScrollBar::handle:vertical {{ 
        background: #c1c1c1; 
        min-height: 0px; 
        border-radius: 5px; 
    }}
    QTextEdit QScrollBar::add-line:vertical,
    QTextEdit QScrollBar::sub-line:vertical {{ 
        height: 0px; 
        subcontrol-origin: margin; 
    }}
    QTextEdit QScrollBar::add-page:vertical, 
    QTextEdit QScrollBar::sub-page:vertical {{ 
        background: none; 
    }}
    QTextEdit QScrollBar:horizontal {{ 
        border: none; 
        background: #f0f0f0; 
        height: 10px; 
        margin: 0px 0px 0px 0px; 
    }}
    QTextEdit QScrollBar::handle:horizontal {{ 
        background: #c1c1c1; 
        min-width: 0px; 
        border-radius: 5px; 
    }}
    QTextEdit QScrollBar::add-line:horizontal,
    QTextEdit QScrollBar::sub-line:horizontal {{ 
        width: 0px; 
        subcontrol-origin: margin; 
    }}
    QTextEdit QScrollBar::add-page:horizontal, 
    QTextEdit QScrollBar::sub-page:horizontal {{ 
        background: none;  
    }}
"""

