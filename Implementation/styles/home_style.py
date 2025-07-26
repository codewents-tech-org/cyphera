home_bg = '#FFFFFF'
home_font_family = 'poppins'
home_font_size = '16px'
home_font_color = 'black'
home_border_size = '2px'
home_border_fg = '#E3E5EC'

action_panel_style = f""" 
                        background-color: {home_bg}; 
                        border: 2px solid {home_border_fg};
                        border-radius: 8px;"
                    """

start_label_style = f"""
                        color: #41484F; 
                        margin-top: 10px; 
                        margin-bottom: 10px; 
                        border: none;
                        font-family: 'Poppins';
                        font-size: 20px;
                        font-weight: bold;
                    """
main_label_stye = f"""
                    color: #41484F; 
                    border: none;
                    background: transparent;
                    font-family: 'Poppins';
                    font-size: 20px;
                    font-weight: bold;
                    """

home_panel_icon_style = f"""
                 border: none;
                 margin-right: 5px;
                 margin-top: 5px;
              """

home_panel_label_style = f"""
                    color: #41484F;
                    border: none;
                    font-family: 'Poppins';
                    font-size: 16px;
                """

home_panel_style = f"""
                        background-color: {home_bg};
                        border: none; 
                        font-family: {home_font_family};
                        font-size: {home_font_size};
                        color: {home_font_color};
                    """
main_panel_label_style = f"""
                        padding: 10px; 
                        background-color: #4CAF50; 
                        color: white; 
                        border: none; 
                        border-radius: 12px;"
                         font-family: 'Poppins';
                        font-size: 20px;
                        font-weight: bold;
                    """
main_panel_input_style = f"""
                            padding: 10px; 
                            border: 2px solid #E3E5EC;
                            border-radius: 12px; 
                            background-color: #FFFFFF; 
                            color: #607182;
                            font-family: 'Poppins';
                            font-size: 12px;
                        """

main_panel_button_style = f"""
                            padding: 10px; 
                            background-color: #17CFCE; 
                            color: white; 
                            border: none; 
                            border-radius: 12px;
                            font-family: 'Poppins';
                            font-size: 12px;
                            font-weight: bold;
                        """

recent_list_stye = f"""
                        color: #333333; 
                        border: none;
                        font-family: 'Poppins';
                        font-size: 11px;
                    """

recent_label_style = f"""
                        color: #333333;
                        margin-top: 20px; 
                        border: none; 
                        margin-bottom: 10px;
                        font-family: 'Poppins';
                        font-size: 14px;
                    """


description_label_style = f"""
                                color: #607182; 
                                line-height: 1.6; 
                                max-width: 600px; 
                                border: none; 
                                margin-bottom: 20px;
                                background: transparent;
                                font-family: 'Poppins';
                                font-size: 14px;
                            """


toggle_button_active_style = """
    QPushButton {
        background-color: #17CFCE;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px;
        font-family: 'Poppins';
        font-size: 12px;
        font-weight: bold;
    }
"""

toggle_button_inactive_style = """
    QPushButton {
        background-color: #F0F0F0;
        color: #333333;
        border: 1px solid #CCCCCC;
        border-radius: 12px;
        padding: 10px;
        font-family: 'Poppins';
        font-size: 12px;
        font-weight: bold;
    }
"""
