
import models.Parameters as P

normal_table_style = f"""
            QTableWidget {{
                background-color: {P.White}; 
                gridline-color: transparent;
                border: none;
                }} 
            QTableWidget::item {{
                font-family: Roboto;
                font-size: 12px;
                background-color: {P.White}; 
                border: none;
                gridline-color: transparent;
                }} 
            QTableWidget::item::selected {{
                background-color: {P.rowhighlight_bg}; 
                color: black; 
                border: none;
                gridline-color: transparent;
                }} 
            QHeaderView::section {{
                font-family: Roboto;
                border: none;
                background-color: white;
                font-size: 20px;
                font-weight: bold;
                }}
            QTableWidget QScrollBar:vertical {{ 
                border: none; 
                background: #f0f0f0;  
                width: 10px; 
                margin: 0px 0px 0px 0px; 
                }}
            QTableWidget QScrollBar::handle:vertical {{ 
                background: #c1c1c1; 
                min-height: 0px; 
                border-radius: 5px; 
                }}
            QTableWidget QScrollBar::add-line:vertical,
            QTableWidget QScrollBar::sub-line:vertical {{ 
                height: 0px; 
                subcontrol-origin: margin; 
                }}
            QTableWidget QScrollBar::add-page:vertical, 
            QTableWidget QScrollBar::sub-page:vertical {{ 
                background: none; 
                }}
            QTableWidget QScrollBar:horizontal {{ 
                border: none; 
                background: #f0f0f0; 
                height: 10px; 
                margin: 0px 0px 0px 0px; 
                }}
            QTableWidget QScrollBar::handle:horizontal {{ 
                background: #c1c1c1; 
                min-width: 0px; 
                border-radius: 5px; 
                }}
            QTableWidget QScrollBar::add-line:horizontal,
            QTableWidget QScrollBar::sub-line:horizontal {{ 
                width: 0px; 
                subcontrol-origin: margin; 
                }}
            QTableWidget QScrollBar::add-page:horizontal, 
            QTableWidget QScrollBar::sub-page:horizontal {{ 
                background: none;  
                }}
            QComboBox::selected{{background-color: transparent; border:none}} 
            QComboBox{{background-color: transparent; border:none}} 
            QComboBox::drop-down {{ width: 0px; border: none; }} 
            QComboBox::down-arrow {{  width: 0px; image: none; }}
            QComboBox:hover {{ background-color: #F7F7F7; color: {P.Black};}} 
            QComboBox QAbstractItemView {{ color: {P.Black}; background-color: white;}}
            QComboBox QAbstractItemView::item:hover {{ color: {P.Black}; background-color: white;}}
            QComboBox QAbstractItemView::item:selected {{ color: {P.Black}; background-color: white; }}
            QPushButton{{background-color: {P.Gray}; border:none}}
        """

table_style = f"""
            QTableWidget {{
                background-color: {P.White}; 
                gridline-color: transparent;
                border: none;
                }} 
            QTableWidget::item {{
                background-color: {P.White}; 
                border: none;
                gridline-color: transparent;
                }} 
            QTableWidget::item::selected {{
                background-color: {P.rowhighlight_bg}; 
                color: black; 
                border: none;
                gridline-color: transparent;
                }} 
            QHeaderView::section {{
                border: none;
                background-color: white;
                font-size: 19px;
                font-weight: bold;
                }}
            QTableWidget QScrollBar:vertical {{ 
                border: none; 
                background: #f0f0f0;  
                width: 10px; 
                margin: 0px 0px 0px 0px; 
                }}
            QTableWidget QScrollBar::handle:vertical {{ 
                background: #c1c1c1; 
                min-height: 0px; 
                border-radius: 5px; 
                }}
            QTableWidget QScrollBar::add-line:vertical,
            QTableWidget QScrollBar::sub-line:vertical {{ 
                height: 0px; 
                subcontrol-origin: margin; 
                }}
            QTableWidget QScrollBar::add-page:vertical, 
            QTableWidget QScrollBar::sub-page:vertical {{ 
                background: none; 
                }}
            QTableWidget QScrollBar:horizontal {{ 
                border: none; 
                background: #f0f0f0; 
                height: 10px; 
                margin: 0px 0px 0px 0px; 
                }}
            QTableWidget QScrollBar::handle:horizontal {{ 
                background: #c1c1c1; 
                min-width: 0px; 
                border-radius: 5px; 
                }}
            QTableWidget QScrollBar::add-line:horizontal,
            QTableWidget QScrollBar::sub-line:horizontal {{ 
                width: 0px; 
                subcontrol-origin: margin; 
                }}
            QTableWidget QScrollBar::add-page:horizontal, 
            QTableWidget QScrollBar::sub-page:horizontal {{ 
                background: none;  
                }}
        """

reset_tablerow_style = f"""QComboBox{{background-color: {P.White}; border:none}} QComboBox::drop-down {{ width: 0px; border: none; }} QComboBox::down-arrow {{  width: 0px; image: none; }}"""

reset_sidebar_style = f"""QPushButton{{background-color: transparent; border:none}}"""

row_highlight_style = f"""  QComboBox{{background-color: {P.rowhighlight_bg}; border:none}} 
                            QComboBox::drop-down {{ width: 0px; border: none; }} 
                            QComboBox::down-arrow {{  width: 0px; image: none; }}
                            QComboBox:hover {{ background-color: #F7F7F7; color: {P.Black};}} 
                            QComboBox QAbstractItemView {{ color: {P.Black}; background-color: white;}}
                            QComboBox QAbstractItemView::item:hover {{ color: {P.Black}; background-color: white;}}
                            QComboBox QAbstractItemView::item:selected {{ color: {P.Black}; background-color: white; }}"""

sidebar_highlight_style = f"""QPushButton{{background-color: {P.Gray}; border:none}}"""
