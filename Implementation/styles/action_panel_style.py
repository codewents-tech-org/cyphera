
action_bg = '#F6F7FB'
action_font_family = 'poppins'
action_font_size = '16px'
action_font_color = 'black'
action_border_size = '2px'
action_border_fg = '#E3E5EC'
label_font_color = '#41484F'
label_font_size = '16px'

action_panel_style = f"""
                        background-color: {action_bg};
                        border: none; 
                        font-family: {action_font_family};
                        font-size: {action_font_size};
                        color: {action_font_color};
                    """

web_view_style = f"""
            background-color: {action_bg}; 
            padding: 10px;
            margin-bottom: 10px;
            border: 2px solid #000;  # You can change the border color and thickness as needed
            border-radius: 8px;  # or 15px for a larger border radius
            
        """

settings_panel_style = f"""
            background-color: white;  /* White background */
            border-radius: 5px;
            padding-top: 10px;        /* Top padding */
            padding-right: 10px;      /* Right padding */
            padding-bottom: 10px;     /* Bottom padding */
            padding-left: 10px;        /* Left padding */
            font-family: {action_font_family};
            font-size: {label_font_size};
            color: {label_font_color};
        """

button_style = f"""
                    padding: 10px;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-family: 'Poppins';
                    font-size: 12px;
                    font-weight: bold;
                """
 