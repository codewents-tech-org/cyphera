
import models.Parameters as P

heading_style = f"""
            font-size: 22px; 
            font-weight: bold; 
            color: {P.Module_bg}; 
            padding: 5px; 
            border: 1px; 
            border-radius: 2px;
            margin-bottom: 10px;
            border-bottom: 3px solid {P.Module_bg};  /* Bottom line */
        """

save_button_style = f"background-color: {P.Module_bg};border: 1px solid #ddd;border-radius: 5px; padding: 5px;"

line_input_style = f"""QLineEdit {{ padding-top: 10px; font-size: 18px; background-color: #F7F7F7;border: 1px;border-radius: 2px;margin-bottom: 20px;border-bottom: 2px solid {P.Module_bg}; }}"""

rt_line_input_style = f"""QLineEdit {{ padding-top: 8px; font-size: 15px; background-color: #F7F7F7;border: 1px;border-radius: 2px;margin-bottom: 10px;border-bottom: 2px solid {P.Module_bg}; }}"""

multiselect_combo_style = f"""
                    QComboBox {{ 
                        padding-top: 10px; 
                        font-size: 18px; 
                        background-color: #F7F7F7; 
                        color: {P.Black};
                        border: 1px;
                        border-radius: 2px;
                        margin-bottom: 20px;
                        border-bottom: 2px solid {P.Module_bg}; }} 
                    QComboBox::drop-down {{ 
                        width: 0px; 
                        border: none; }} 
                    QComboBox::down-arrow {{ 
                        width: 0px; 
                        image: none; }} 
                    QComboBox:hover {{ 
                        background-color: #F7F7F7; 
                        color: {P.Black}; 
                    }} 
                    QComboBox QAbstractItemView {{ 
                        color: {P.Black}; /* Set the default text color of items */
                        background-color: #F7F7F7; /* Set background for the item list */
                    }}
                    QComboBox QAbstractItemView::item:hover {{ 
                        color: {P.Black}; /* Set text color when hovering */
                        background-color: #EAEAEA; /* Optional: background color of hovered items */
                    }}
                    QComboBox QAbstractItemView::item:selected {{ 
                        color: {P.Black}; /* Set text color for selected items */
                        background-color: #D3D3D3; /* Optional: background color for selected items */
                    }}
                    QComboBox QAbstractItemView::item:QToolTip {{ 
                        color: {P.Black}; /* Set text color when hovering */
                        background-color: #EAEAEA; /* Optional: background color of hovered items */
                    }}
                    QComboBox:QToolTip {{
                        color: {P.Black}; /* Set tooltip text color to black */
                        background-color: #F7F7F7; /* Set tooltip background color */
                        border: 1px solid {P.Module_bg}; /* Optional: border for the tooltip */
                    }} """

rt_multiselect_combo_style = f"""
                    QComboBox {{ 
                        padding-top: 8px; 
                        font-size: 15px; 
                        background-color: #F7F7F7; 
                        color: {P.Black};
                        border: 1px;
                        border-radius: 2px;
                        margin-bottom: 10px;
                        border-bottom: 2px solid {P.Module_bg}; }} 
                    QComboBox::drop-down {{ 
                        width: 0px; 
                        border: none; }} 
                    QComboBox::down-arrow {{ 
                        width: 0px; 
                        image: none; }} """

multiline_input_style = f"""QTextEdit {{ padding-top: 10px; font-size: 18px; background-color: #F7F7F7;border: 1px;border-radius: 2px;margin-bottom: 20px;border-bottom: 2px solid {P.Module_bg}; }}"""
