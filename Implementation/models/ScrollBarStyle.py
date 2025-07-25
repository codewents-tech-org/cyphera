
GraphicsView_ScrollBar_style = f"""
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

Scrollbar_ScrollBar_style = f"""
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

Scrollbar_ScrollingBar_style = """
QScrollBar:vertical {
    border: none;
    background: #f0f0f0;
    width: 10px;
    margin: 0px 0px 0px 0px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #c1c1c1;
    min-height: 40px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    subcontrol-origin: margin;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
QScrollBar:horizontal {
    border: none;
    background: #f0f0f0;
    height: 10px;
    margin: 0px 0px 0px 0px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #c1c1c1;
    min-width: 40px;
    border-radius: 5px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
    subcontrol-origin: margin;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
"""
