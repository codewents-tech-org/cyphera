from PyQt5.QtGui import QFont

node_bg = "#FFFFFF"
node_border_color = "#CCD2E3"
node_font_family = "poppins"
node_font_size = "10px"
node_font_color = "#607182"

headnode_sidebar_color = "#14B8FF"
intermediatenode_sidebar_color = "#2883BC"
leafnode_sidebar_color = "#9C28BC"
selectedleafnode_color = "#CCD2E3"
controlnode_sidebar_color = "#EF9D92"
technicalnode_sidebar_color = "#B4DF5A"

High_AFR_Font_color = "#0097b2"
High_AFR_bg_color = "#0097b2"
High_AFR_border_color = "#0097b2"
Medium_AFR_Font_color = "#0097b2"
Medium_AFR_bg_color = "#0cc0df"
Medium_AFR_border_color = "#0097b2"
Low_AFR_Font_color = "#0097b2"
Low_AFR_bg_color = "#5ce1e6"
Low_AFR_border_color = "#0097b2"
VeryLow_AFR_Font_color = "#0097b2"
VeryLow_AFR_bg_color = "#cefdff"
VeryLow_AFR_border_color = "#0097b2"
arrow_highlight_color = "#E5B511"
arrow_color = "#151515"


node_id_font = QFont("poppins", 10, QFont.Bold)

headnode_box_style = f"""
                QPushButton {{
                background: {node_bg};
                font-family: {node_font_family};
                font-size: 10px;
                border: 2px solid {node_border_color};
                border-radius: 10px;
                }}
        """

headnode_side_box_style = f"""
                QPushButton {{
                background-color: {headnode_sidebar_color};
                font-family: {node_font_family};
                font-size: 10px;
                border-left-top-radius: 10px;
                border-left-bottom-radius: 10px;
                }}
        """

leafnode_box_style = f"""
                QPushButton {{
                background-color: {node_bg};
                font-family: {node_font_family};
                font-size: 10px;
                border: 2px solid {node_border_color};
                border-radius: 10px;
                }}
        """

selectedleafnode_box_style = f"""
                QPushButton {{
                background-color: {node_bg};
                font-family: {node_font_family};
                font-size: 10px;
                border: 3px solid {leafnode_sidebar_color};
                border-radius: 10px;
                }}
        """