import os
from lxml import etree

def change_svg_stroke_color(svg_path, new_color):
    # Ensure the input file is an SVG
    if not svg_path.lower().endswith('.svg'):
        print(f"Error: The file {svg_path} is not an SVG file.")
        return
    
    try:
        # Parse the SVG file
        tree = etree.parse(svg_path)
        root = tree.getroot()

        # Loop through all elements in the SVG file
        for elem in root.iter():
            if 'stroke' in elem.attrib:
                elem.attrib['stroke'] = new_color
            # if 'fill' in elem.attrib:
            #     elem.attrib['fill'] = new_color
        
        # Save the modified SVG file
        with open(svg_path, 'wb') as f:
            tree.write(f)
        # print(f"SVG file saved to {svg_path}")
    
    except etree.XMLSyntaxError as e:
        print(f"Error parsing SVG file: {e}")
    except Exception as e:
        print(f"Error: {e}")