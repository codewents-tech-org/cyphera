
footer_bg = '#17CFCE'
footer_height = '30px'
footer_font_family = 'poppins'
footer_font_size = '16px'
footer_font_color = 'white'
footer_line_border_size = '2px'

footer_style = f'''QFrame {{
                        background-color: {footer_bg};
                        height: {footer_height};
                        border: none;
                    }}
                    QLabel {{
                        font-family: {footer_font_family};
                        font-size: {footer_font_size};
                        color: {footer_font_color};
                    }}
                '''

footer_line_style = f"border: {footer_line_border_size} solid {footer_font_color};"

footer_button_style = f"""
                        QPushButton {{
                            background-color: transparent;  /* No background */
                            border: none;                  /* No border */
                            padding: 0px;                  /* Remove padding */
                        }}
                        """
