
from PyQt5.QtGui import QFont

table_bg = '#FFFFFF'
table_heading_bg = '#E7E9EE'
table_heading_font_size = '16px'
table_selected_row_bg = '#F0F2F8'
table_border_fg = '#E3E5EC'
table_border_size = '2px'
table_font_color = '#41484F'
table_font_family = 'Poppins'
table_font_size = '12px'
table_row_height = '50px'
table_cell_padding_size = '5px'


table_style = f"""
            QTableWidget {{
                background-color: {table_bg}; 
                font-family: {table_font_family};
                gridline-color: transparent;
                border: 2px solid {table_border_fg};
                padding: 0px;
                border-radius: 10px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                }} 
            QTableWidget::item {{
                font-family: {table_font_family};
                font-size: {table_font_size};
                background-color: {table_bg}; 
                color: {table_font_color}; 
                border: none;
                border-bottom: {table_border_size} solid {table_border_fg};
                gridline-color: transparent;
                padding-left: {table_cell_padding_size};
                border-radius: 0px;
                }} 
            QTableWidget::item::selected {{
                background-color: {table_selected_row_bg}; 
                color: {table_font_color}; 
                gridline-color: transparent;
                }} 
            QHeaderView::section {{
                font-family: {table_font_family};
                border: 0px solid transparent;
                background-color: {table_heading_bg};
                font-size: {table_heading_font_size};
                font-weight: bold;
                padding: 0px;
                padding-left: 5px;
                
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
            QComboBox{{background-color: transparent; color: {table_font_color};  border:none}} 
            QComboBox::drop-down {{ width: 0px; border: none; }} 
            QComboBox::down-arrow {{  width: 0px; image: none; }}
            QComboBox:hover {{ background-color: #F7F7F7; color: black;}} 
           
            QPushButton{{background-color: {table_bg}; border:none}}
        """

tree_style = f"""
    QTreeWidget {{
        border: none;  /* Ensure the whole tree widget has no border */
        background: {table_bg};
    }}
    
    QTreeWidget::item:selected {{
        background: {table_selected_row_bg}; /* Change the background color when selected */
        color: {table_font_color};  /* Text color for the selected item */
    }}
    
    QTreeWidget::item {{
        border: none;  /* Remove border for the individual items */
        padding: 5px;
    }}
    
    QTreeWidget::item:!selected {{
        background: transparent;  /* Make the background transparent when not selected */
    }}

    QTreeWidget QScrollBar:vertical {{
        border: none; 
        background: #f0f0f0;  
        width: 10px; 
        margin: 0px 0px 0px 0px; 
    }}
    QTreeWidget QScrollBar::handle:vertical {{
        background: #c1c1c1; 
        min-height: 0px; 
        border-radius: 5px; 
    }}
    QTreeWidget QScrollBar::add-line:vertical,
    QTreeWidget QScrollBar::sub-line:vertical {{
        height: 0px; 
        subcontrol-origin: margin; 
    }}
    QTreeWidget QScrollBar::add-page:vertical, 
    QTreeWidget QScrollBar::sub-page:vertical {{
        background: none; 
    }}
    QTreeWidget QScrollBar:horizontal {{
        border: none; 
        background: #f0f0f0; 
        height: 10px; 
        margin: 0px 0px 0px 0px; 
    }}
    QTreeWidget QScrollBar::handle:horizontal {{
        background: #c1c1c1; 
        min-width: 0px; 
        border-radius: 5px; 
    }}
    QTreeWidget QScrollBar::add-line:horizontal,
    QTreeWidget QScrollBar::sub-line:horizontal {{
        width: 0px; 
        subcontrol-origin: margin; 
    }}
    QTreeWidget QScrollBar::add-page:horizontal, 
    QTreeWidget QScrollBar::sub-page:horizontal {{ 
        background: none;  
    }}
"""

report_tree_style = f"""
        QTreeView QScrollBar:vertical {{ 
            border: none; 
            background: #f0f0f0;  
            width: 10px; 
            margin: 0px 0px 0px 0px; 
        }}

        QTreeView QScrollBar::handle:vertical {{ 
            background: #c1c1c1; 
            min-height: 0px; 
            border-radius: 5px; 
        }}

        QTreeView QScrollBar::add-line:vertical,
        QTreeView QScrollBar::sub-line:vertical {{ 
            height: 0px; 
        }}

        QTreeView QScrollBar::add-page:vertical, 
        QTreeView QScrollBar::sub-page:vertical {{ 
            background: none; 
        }}

"""

report_table_style = f"""
    QTableWidget {{
        gridline-color: transparent;
        border: 2px solid {table_border_fg};
        padding: 0px;
        border-radius: 10px;
    }}
    QHeaderView::section {{
        font-family: {table_font_family};
        border: 0px solid transparent;
        background-color: {table_heading_bg};
        font-size: {table_heading_font_size};
        font-weight: bold;
        padding: 0px;
        padding-left: 5px;
        color: {table_font_color};
    }}
    QTableWidget::item {{
        font-family: {table_font_family};
        font-size: {table_font_size};
        color: {table_font_color}; 
        padding: {table_cell_padding_size};
        height: {table_row_height};
    }}
    QTableWidget::item::selected {{
                background-color: {table_selected_row_bg}; 
                color: {table_font_color}; 
                gridline-color: transparent;
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
