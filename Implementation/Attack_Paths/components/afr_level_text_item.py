"""
Module: afr level text item      \n 
File: afr_level_text_item.py      \n
Layer: UI / Graphics Items    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-07-02     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Provides a visual text item for AFR/AF level inside attack/control trees,
rendered with color-coded styling and ellipsis for overflow text.

Description:
------------
- Display level as a rounded badge (text + color)
- Auto-ellipsize overflow
- Provide fixed width and height
- Determine colors dynamically based on level text

Responsibilities
----------------
- Render a visually distinct label for qualitative AFR/AF levels (e.g., Low, Medium, High)
- Display rounded rectangle background with dynamic coloring
- Auto-ellipsize text if it exceeds the label width
- Consistently sized across the tree nodes for layout harmony

Dependencies:
-------------
- PyQt5.QtWidgets.QGraphicsTextItem
- PyQt5.QtGui (QFont, QPainter, QColor, QBrush)
- PyQt5.QtCore (Qt, QRectF)
- styles.tree_style: project-wide color theme definitions

Classes:
-------------
- AFR_level (QGraphicsTextItem)
   - Renders AFR label with background, border, and centered text

Limitations
-----------
- Fixed width/height; does not auto-resize for long content
- Requires theme variables from `styles.tree_style`
- No dynamic font scaling for smaller canvas sizes

Improvements
------------
- Support hover/highlight animation
- Add tooltips for full text visibility
- Auto-resize with content length or support multi-line wrapping
- Expose signal for click interaction if needed in the future

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-07-02           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QFont, QPainterPath, QPen, QColor, QBrush, QFontMetrics, QTextOption
from PyQt5.QtCore import Qt, QRectF
import styles.tree_style as tree_style

class AFR_level(QGraphicsTextItem):
    """
    Displays the visual label for the assessment factor level (AFR/AF value).

    This component renders a colored rectangle with text, used to indicate
    the qualitative level (e.g., Low, Medium, High) associated with a node’s
    risk, attack, or assessment factor in various tree structures.
    """
    def __init__(self, text=''):
        """
        Initializes the AFR level label item.

        Args:
            text (str): The AFR level text (e.g., 'Low', 'High')
        """
        super().__init__()
        self.setTextWidth(80)
        self.full_text = text
        font = QFont("Roboto", 8, QFont.Bold)
        self.setFont(font)
        self.setDefaultTextColor(Qt.black)
        self.update_display_text()
    
    def boundingRect(self):
        """
        Returns a fixed-size rectangle for the badge.

        Returns:
            QRectF: Fixed width and height (80 x 30 px)
        """
        return QRectF(0, 0, 80, 30)
    
    def setPlainText(self, text):
        """
        Sets and updates the full text.

        Args:
            text (str): AFR level (e.g., "High")
        """
        self.full_text = text
        super().setPlainText(text)
        self.update_display_text()

    def update_display_text(self):
        """
        Ellipsizes and updates the display text to fit fixed width.
        """
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.full_text, Qt.ElideRight, 80, 0)
        super().setPlainText(elided)
        self.update()

    def paint(self, painter, option, widget=None):
        """
        Paints the background badge and centered text.
        """
        rect = self.boundingRect()

        bg_color, border_color, text_color = self.get_colors_based_on_text()
        bg_color.setAlpha(50)

        painter.setBrush(QBrush(bg_color))
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

        pen = QPen(border_color, 1)
        painter.setPen(pen)
        painter.drawPath(path)

        # text_option = QTextOption(Qt.AlignCenter)
        # text_option.setWrapMode(QTextOption.NoWrap)
        text_option = QTextOption(Qt.AlignCenter)
        text_option.setWrapMode(QTextOption.NoWrap)
        painter.drawText(rect, self.toPlainText(), text_option)
        painter.setPen(text_color)
        # painter.drawText(rect, self.full_text, text_option)

    def get_colors_based_on_text(self):
        """
        Maps the level text to background, border, and font colors.

        Returns:
            Tuple[QColor, QColor, QColor]: Background, border, and text colors.
        """
        val = self.full_text.lower()
        mapping = {
            'high': ("High_AFR_bg_color", "High_AFR_border_color", "High_AFR_Font_color"),
            'medium': ("Medium_AFR_bg_color", "Medium_AFR_border_color", "Medium_AFR_Font_color"),
            'low': ("Low_AFR_bg_color", "Low_AFR_border_color", "Low_AFR_Font_color"),
            'very low': ("VeryLow_AFR_bg_color", "VeryLow_AFR_border_color", "VeryLow_AFR_Font_color"),
        }
        keys = mapping.get(val, ("node_bg", "node_bg", "node_bg"))
        return tuple(QColor(getattr(tree_style, k)) for k in keys)
    