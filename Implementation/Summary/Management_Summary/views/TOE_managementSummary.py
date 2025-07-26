# Analysis_action.py
                             
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QMessageBox, QMenuBar, QAction, QHeaderView, QTabWidget, QMenu,QMainWindow,QSizePolicy,
    QLineEdit, QLabel, QSplitter, QFrame, QToolTip, QGraphicsDropShadowEffect, QStyledItemDelegate, QToolBar,
    QGridLayout, QFileDialog, QStackedWidget, QButtonGroup, QSpacerItem, QTextEdit, QToolButton, QStyle,
    QFontComboBox,QWidgetAction, QColorDialog, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QDialog,
    QSpinBox,QInputDialog, QScrollArea, QTextBrowser
)
from PyQt5.QtGui import (
    QIcon, QPainter, QCursor, QFont, QColor, QBrush, QStandardItemModel, QStandardItem, 
    QTextCharFormat, QTextCursor, QTextListFormat, QTextImageFormat, QPainter, QTextTableFormat,QImage, 
    QTextLength, QPen, QPixmap, QTextTableCellFormat
)
from PyQt5.QtCore import QTimer, Qt, QSize, QRect, QRectF, pyqtSlot, QPoint
import sqlite3
import sys
import os
import models.Parameters as P
import models.helper as helper
import controllers.DatabaseCreator as DB
from PyQt5.QtGui import QTextBlockFormat
from functools import partial
from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import QUrl
import docx
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import RGBColor
from collections import defaultdict
from docx.shared import Inches, Pt
from reportlab.lib.pagesizes import letter
import components.toolbarhighlight as TH
from Summary.Management_Summary.views.TOE_managementSummary_toolbar import create_toolbar
import sqlite3
from docx import Document
from bs4 import BeautifulSoup  # To parse HTML content
import datetime
import styles.toolbar_style as toolbar_style
import logging
import utils.interface_utils as interfaces
import time 
from components.loading_dialog import RoundLoader
logger = logging.getLogger(__name__)
class TOEDescription(QWidget):
    def __init__(self, parent=None):
        logger.info("Scope Description class")
        super().__init__(parent)
       
        # ✅ Initialize selection tracking to prevent AttributeError
        self.is_selecting = False
        self.current_font_family = "Arial"
        self.current_font_size = 8
        self.current_bold = False
        self.current_italic = False
        self.current_underline = False
        self.current_font_color = QColor("black")
        self.current_highlight_color = QColor("white")
        self.current_alignment = "Left"
        self.update_timer = QTimer()  # ✅ Timer for delayed toolbar update
        self.update_timer.setSingleShot(True)  # Ensures it runs only once after timeout
        self.update_timer.timeout.connect(self.update_toolbar_state) 
        self.mixed_bold_attempted = False  # Call toolbar update when timer expires
       
        self.initUI()
        self.text_edit.setFixedHeight(400)  
        
        self.text_edit.textChanged.connect(self.set_unsaved_changes)

    def update_toolbar_state(self):
        """Update toolbar buttons based on the current cursor selection and update stored values while preventing unwanted color changes."""
        try:
            if not hasattr(self, "text_edit"):
                print("❌ Error: text_edit not found")
                return

            cursor = self.text_edit.textCursor()
            table = cursor.currentTable()

            # Detect if selection contains an image
            selected_html = cursor.selection().toHtml()
            contains_image = "<img " in selected_html

            if table:
                # Handle table cell text updates
                cell_cursor = table.cellAt(cursor).firstCursorPosition()
                cursor.setPosition(cell_cursor.position())

            if cursor.hasSelection():
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                cursor.setPosition(start, QTextCursor.MoveAnchor)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                fmt = cursor.charFormat()
                block_fmt = cursor.blockFormat()

                # Check for mixed font sizes in selection
                cursor.setPosition(start, QTextCursor.MoveAnchor)
                first_size = cursor.charFormat().fontPointSize()
                mixed_font_sizes = False
                while cursor.position() < end:
                    cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                    if cursor.charFormat().fontPointSize() != first_size:
                        mixed_font_sizes = True
                        break  # Stop checking once a difference is detected
            else:
                # When no selection is present, use the QTextEdit's currentCharFormat
                fmt = self.text_edit.currentCharFormat()
                block_fmt = cursor.blockFormat()
                mixed_font_sizes = False  # No selection means no mixed sizes
                # Define start and end as current cursor position to avoid undefined variable error
                start = cursor.position()
                end = cursor.position()

            # Prevent unwanted text color change when an image is nearby
            if contains_image:
                print("🖼️ Image detected in selection! Preventing automatic color override.")
                return  # Skip applying format if image is involved

            # Get Font Properties (Only if selection does NOT contain an image)
            font = fmt.font()
            if not mixed_font_sizes:
                self.current_font_size = font.pointSize() if font.pointSize() > 0 else self.text_edit.fontPointSize()
                # --- ADDED LINES: Update the combo box to show the correct font size ---
                if hasattr(self, "font_size_combo"):
                    self.font_size_combo.blockSignals(True)
                    self.font_size_combo.setCurrentText(str(int(self.current_font_size)))
                    self.font_size_combo.blockSignals(False)
            else:
                print("⚠️ Mixed font sizes detected! Keeping previous font size.")

            self.current_bold = font.bold()
            self.current_italic = font.italic()
            self.current_underline = font.underline()
            self.current_font_family = font.family()

            # Preserve text colors per character instead of setting one global color
            mixed_colors = False
            cursor.setPosition(start, QTextCursor.MoveAnchor)
            first_color = cursor.charFormat().foreground().color()
            while cursor.position() < end:
                cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                current_color = cursor.charFormat().foreground().color()
                if current_color != first_color:
                    mixed_colors = True
                    break  # Stop checking once a different color is detected

            if mixed_colors:
                print("⚠️ Mixed text colors detected! Preserving individual colors.")
                self.current_font_color = None  # Keep existing colors
            else:
                self.current_font_color = first_color  # Apply the detected single color

            # Detect bullets and numbering in the current block
            block = cursor.block()
            list_format = block.textList()
            self.current_list_format = None

            # Get Alignment & Update Icon
            alignment = block_fmt.alignment()
            alignment_icon = "assets/Images/left_align.png"
            if alignment == Qt.AlignLeft:
                self.current_alignment = "Left"
                alignment_icon = P.left_align_icon
            elif alignment == Qt.AlignCenter:
                self.current_alignment = "Center"
                alignment_icon = P.center_align_icon
            elif alignment == Qt.AlignRight:
                self.current_alignment = "Right"
                alignment_icon = P.right_align_icon
            elif alignment == Qt.AlignJustify:
                self.current_alignment = "Justified"
                alignment_icon = P.justify_icon
            else:
                self.current_alignment = "Unknown"

            # Preserve highlight color without overriding individual character colors
            self.current_highlight_color = fmt.background().color()

             # Update toolbar buttons
            if hasattr(self, "bold_button"):
                self.bold_button.setChecked(self.current_bold)
            if hasattr(self, "italic_button"):
                fmt = self.text_edit.currentCharFormat()
                is_italic = fmt.fontItalic()
                self.italic_button.setChecked(is_italic)
                self.italic_button.setStyleSheet(
                    toolbar_style.toolbar_button_hover_style if is_italic 
                    else toolbar_style.toolbar_button_style
                )
            if hasattr(self, "underline_button"):
                self.underline_button.setChecked(self.current_underline)
            if hasattr(self, "highlight_button"):
                # Only consider current character’s background 
                fmt = self.text_edit.currentCharFormat()
                is_highlighted = fmt.background().color() == QColor("#ffff00")
                self.highlight_button.setChecked(is_highlighted)
                self.highlight_button.setStyleSheet(
                    toolbar_style.toolbar_button_hover_style if is_highlighted 
                    else toolbar_style.toolbar_button_style
                )

            if hasattr(self, "align_button"):
                self.align_button.setIcon(QIcon(alignment_icon))
            # Update font style detection
            if self.current_bold and self.current_font_size >= 14:
                self.current_font_style = "Heading"
            else:
                self.current_font_style = "Normal"

        except Exception as e:
            print(f"❌ Failed to update toolbar state: {e}")







    def on_selection_change(self):
        """Detect selection changes and update the toolbar state properly, including table, image, and mixed content selection."""

        # Prevent duplicate calls
        if not hasattr(self, "_selection_timer_running"):
            self._selection_timer_running = False  # ✅ Initialize flag

        if self._selection_timer_running:
            return  # ✅ Exit if already scheduled

        cursor = self.text_edit.textCursor()
        table = cursor.currentTable()

        # Extract HTML selection for debugging and detection
        if cursor.hasSelection():
            selected_html = cursor.selection().toHtml()
            print("\n🔍 Selected HTML Content:\n", selected_html)  # Debugging

            # Detect if an image is selected
            contains_image = "<img " in selected_html
            if contains_image:
                print("✅ Image detected in selection! Preventing unwanted formatting.")
                return  # ✅ Skip further formatting updates if an image is in selection

        if table:
            # Handle cases where only table text is selected
            if cursor.hasSelection():
                print("📌 Selection inside table detected, updating toolbar.")
            else:
                # ✅ If cursor is inside a table but no selection, update toolbar without moving cursor
                print("📌 Cursor inside table cell (no selection), updating toolbar.")

        # ✅ Apply 300ms delay to prevent rapid multiple calls
        self._selection_timer_running = True
        self.update_timer.start(300)

        def reset_timer_flag():
            self._selection_timer_running = False  # ✅ Allow the next selection change event

        QTimer.singleShot(310, reset_timer_flag)  # ✅ Reset flag after 310ms

    def initUI(self):
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            self.setLayout(main_layout)

            

            # ✅ Initialize QTextEdit first
            self.text_edit = QTextEdit(self)
            self.text_edit = CleanTextEdit(self)


            # ✅ Set default font to Arial 8pt
            default_font = QFont("Arial", 8)
            self.text_edit.setFont(default_font)  # ✅ Ensures UI text is in 8pt

            
            # ✅ Set Default QTextCharFormat with 8pt and white background explicitly
            fmt = QTextCharFormat()
            fmt.setFontPointSize(8)
            fmt.setBackground(QColor("white"))  # ✅ Ensure no black background
            self.text_edit.setCurrentCharFormat(fmt)

            self.text_edit.setFont(QFont("Arial", 8))
            self.text_edit.setFontPointSize(8)
            self.text_edit.setCurrentFont(QFont("Arial", 8))

            self.text_edit.setStyleSheet("""
    QTextEdit {
        background-color: rgb(255, 255, 255);
        color: black;
        font-size: 8pt;
        padding: 5px;
        border: 1px solid rgb(211, 211, 211);
        border-radius: 8px;
    }

    /* ✅ Custom Styled Vertical Scrollbar */
    QTextEdit QScrollBar:vertical {
        border: none;
        background: #f0f0f0;  
        width: 10px;
        margin: 0px 0px 0px 0px;
    }

    QTextEdit QScrollBar::handle:vertical {
        background: #c1c1c1;
        min-height: 20px;
        border-radius: 5px;
    }

    QTextEdit QScrollBar::add-line:vertical,
    QTextEdit QScrollBar::sub-line:vertical {
        height: 0px;
        subcontrol-origin: margin;
    }

    QTextEdit QScrollBar::add-page:vertical,
    QTextEdit QScrollBar::sub-page:vertical {
        background: none;
    }

    /* ✅ Custom Styled Horizontal Scrollbar */
    QTextEdit QScrollBar:horizontal {
        border: none;
        background: #f0f0f0;
        height: 10px;
        margin: 0px 0px 0px 0px;
    }

    QTextEdit QScrollBar::handle:horizontal {
        background: #c1c1c1;
        min-width: 20px;
        border-radius: 5px;
    }

    QTextEdit QScrollBar::add-line:horizontal,
    QTextEdit QScrollBar::sub-line:horizontal {
        width: 0px;
        subcontrol-origin: margin;
    }

    QTextEdit QScrollBar::add-page:horizontal,
    QTextEdit QScrollBar::sub-page:horizontal {
        background: none;
    }
""")

# ✅ Force Update to Apply Styles
            self.text_edit.repaint()
            self.text_edit.update()
           

            # ✅ Apply default styles after setting focus
            self.text_edit.setFocus()
            self.text_edit.setFontPointSize(8)

            # ✅ Connect selection change to timer instead of updating immediately
            self.text_edit.cursorPositionChanged.connect(self.on_selection_change)
            self.text_edit.selectionChanged.connect(self.on_selection_change)
            self.text_edit.document().undoAvailable.connect(lambda available: QTimer.singleShot(100, self.update_toolbar_state))
            self.htmlfilepath="report/TOE_Description_summary.html"



            # ✅ Create toolbar before updating state
            buttons = {
                "Italic": (P.italic_icon, "Italic", lambda: self.toggle_italic()),
                "Save": (P.save_icon, "Save", lambda: self.submit_changes(self.htmlfilepath)),
                "Refresh": (P.Reload_icon, "Refresh", lambda: self.load_from_database(1)),
                "Font Color": (P.text_color_icon, "Font Color", self.select_font_color),
                "Highlight": (P.highlight_icon, "Highlight", self.select_highlight_color),
                "Insert Picture": (P.insert_image_icon, "Insert Picture", self.insert_picture),
                "Bullets": (P.bullet_index_icon, "Bullets", self.show_bullet_menu),
                "Numbering": (P.number_index_icon, "Numbering", self.show_numbering_menu),
                "Bold": (P.bold_icon, "Bold", lambda: self.toggle_bold()),
                "Left Align": (P.left_align_icon, "Left Align", lambda: self.change_alignment(Qt.AlignLeft)),
                "Center Align": (P.center_align_icon, "Center Align", lambda: self.change_alignment(Qt.AlignCenter)),
                "Right Align": (P.right_align_icon, "Right Align", lambda: self.change_alignment(Qt.AlignRight)),
                "Justify": (P.justify_icon, "Justify", lambda: self.change_alignment(Qt.AlignJustify)),
                "Insert Table": (P.insert_table_icon, "Insert Table", self.insert_table),
                "Insert Row Above": (P.insert_row_above_icon, "Insert Row Above", lambda: self.add_row_above(self.text_edit.textCursor())),
                "Insert Row Below": (P.insert_row_below_icon, "Insert Row Below", lambda: self.add_row_below(self.text_edit.textCursor())),
                "Delete Row": (P.delete_row_icon, "Delete Row", lambda: self.delete_row(self.text_edit.textCursor())),
                "Insert Column Left": (P.insert_column_left_icon, "Insert Column Left", lambda: self.add_column_left(self.text_edit.textCursor())),
                "Insert Column Right": (P.insert_column_right_icon, "Insert Column Right", lambda: self.add_column_right(self.text_edit.textCursor())),
                "Delete Column": (P.delete_column_icon, "Delete Column", lambda: self.delete_column(self.text_edit.textCursor())),
            }
            
            create_toolbar(self, buttons)  # ✅ Ensure toolbar is created before updating UI
            main_layout.addWidget(self.toolbar)
            # Create a wrapper layout for QTextEdit
            text_edit_layout = QVBoxLayout()
            text_edit_layout.setContentsMargins(10, 10, 10, 10)  # ✅ Adds spacing around QTextEdit
            text_edit_layout.setSpacing(0)

            # Add QTextEdit to this layout
          
            text_edit_layout.addWidget(self.text_edit)

            # Create a frame to apply the margins
            text_edit_frame = QFrame(self)
            text_edit_frame.setStyleSheet("""
                    QFrame {
                        border: none;  /* ✅ No border for the outer frame */
                        background-color: transparent;
                    }
                """)
            

            text_edit_frame.setLayout(text_edit_layout)

            # Add this frame to the main layout
            main_layout.addWidget(text_edit_frame)



            # ✅ Apply correct default font size
            self.text_edit.setFocus()  # ✅ Ensure editor is focused before applying the format

            fmt = QTextCharFormat()
            fmt.setFontPointSize(8)
            self.text_edit.setCurrentCharFormat(fmt)  # ✅ Ensures newly typed text is 8pt

            # ✅ Ensure the toolbar font size dropdown reflects the correct font
            if hasattr(self, "font_size_combo"):
                self.font_size_combo.setCurrentText("8")  # ✅ Update UI dropdown to 8pt

            # ✅ Assign keyboard shortcuts for formatting actions
            self.text_edit.setShortcutEnabled(True)

            if hasattr(self, "current_font_family"):
                self.text_edit.setFont(QFont(self.current_font_family, self.current_font_size))
            else:
                print("⚠️ `current_font_family` is missing! Defaulting to Arial.")
                self.text_edit.setFont(QFont("Arial", self.current_font_size))


            # ✅ Create the "Save" shortcut (Ctrl+S)
            self.shortcut_save = QAction("Save", self)
            self.shortcut_save.setShortcut("Ctrl+S")
            self.shortcut_save.triggered.connect( lambda: self.submit_changes(self.htmlfilepath))
            self.addAction(self.shortcut_save)  # ✅ Adds the shortcut to the widget

            
            self.text_edit.shortcut_bold = QAction("Bold", self)
            self.text_edit.shortcut_bold.setShortcut("Ctrl+B")  #  Bold shortcut
            self.text_edit.shortcut_bold.triggered.connect(lambda: self.toggle_bold())
            self.addAction(self.text_edit.shortcut_bold)

            self.text_edit.shortcut_italic = QAction("Italic", self)
            self.text_edit.shortcut_italic.setShortcut("Ctrl+I")  #  Italic shortcut
            self.text_edit.shortcut_italic.triggered.connect(self.toggle_italic)
            self.addAction(self.text_edit.shortcut_italic)

            self.text_edit.shortcut_highlight = QAction("Highlight", self)
            self.text_edit.shortcut_highlight.setShortcut("Ctrl+H")  #  Highlight shortcut
            self.text_edit.shortcut_highlight.triggered.connect(self.select_highlight_color)
            self.addAction(self.text_edit.shortcut_highlight)

            # ✅ Update toolbar state after initialization
            self.update_toolbar_state()

            
            self.text_edit.setStyleSheet("""
    QTextEdit {
        background-color: rgb(255, 255, 255);
        color: black;
        font-size: 8pt;
        padding: 5px;
        border: 1px solid rgb(211, 211, 211);
        border-radius: 8px;
    }

    /* ✅ Custom Styled Vertical Scrollbar */
    QTextEdit QScrollBar:vertical {
        border: none;
        background: #f0f0f0;  
        width: 10px;
        margin: 0px 0px 0px 0px;
    }

    QTextEdit QScrollBar::handle:vertical {
        background: #c1c1c1;
        min-height: 20px;
        border-radius: 5px;
    }

    QTextEdit QScrollBar::add-line:vertical,
    QTextEdit QScrollBar::sub-line:vertical {
        height: 0px;
        subcontrol-origin: margin;
    }

    QTextEdit QScrollBar::add-page:vertical,
    QTextEdit QScrollBar::sub-page:vertical {
        background: none;
    }

    /* ✅ Custom Styled Horizontal Scrollbar */
    QTextEdit QScrollBar:horizontal {
        border: none;
        background: #f0f0f0;
        height: 10px;
        margin: 0px 0px 0px 0px;
    }

    QTextEdit QScrollBar::handle:horizontal {
        background: #c1c1c1;
        min-width: 20px;
        border-radius: 5px;
    }

    QTextEdit QScrollBar::add-line:horizontal,
    QTextEdit QScrollBar::sub-line:horizontal {
        width: 0px;
        subcontrol-origin: margin;
    }

    QTextEdit QScrollBar::add-page:horizontal,
    QTextEdit QScrollBar::sub-page:horizontal {
        background: none;
    }
""")

# ✅ Force Update to Apply Styles
            self.text_edit.repaint()
            self.text_edit.update()




            self.text_edit.setFont(QFont(self.current_font_family, self.current_font_size))
            self.text_edit.setFontPointSize(self.current_font_size)
            self.load_from_database(1)
    
    def toggle_italic(self):
        """Toggle italic formatting while preserving the original text styling."""
        try:
            cursor = self.text_edit.textCursor()

            # 1) No selection => Toggle the currentCharFormat only.
            if not cursor.hasSelection():
                current_fmt = self.text_edit.currentCharFormat()
                is_italic = current_fmt.fontItalic()
                new_italic_state = not is_italic
                current_fmt.setFontItalic(new_italic_state)
                self.text_edit.setCurrentCharFormat(current_fmt)
                self.current_italic = new_italic_state

            # 2) Selection => Check if the entire selection is italic or not.
            else:
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                temp_cursor = self.text_edit.textCursor()
                temp_cursor.setPosition(start)
                temp_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                
                # Check if all characters match the italic state of the first character.
                first_char_italic = temp_cursor.charFormat().fontItalic()
                all_same = True
                while temp_cursor.position() < end:
                    temp_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                    if temp_cursor.charFormat().fontItalic() != first_char_italic:
                        all_same = False
                        break

                # Uniform toggle: if the entire selection is uniformly italic, toggle it.
                new_italic_state = not first_char_italic
                fmt = QTextCharFormat()
                fmt.setFontItalic(new_italic_state)
                cursor.mergeCharFormat(fmt)
                self.text_edit.setTextCursor(cursor)
                self.current_italic = new_italic_state

            # Update the italic button, if present.
            if hasattr(self, "italic_button"):
                self.italic_button.setChecked(self.current_italic)
                self.italic_button.setStyleSheet(
                    toolbar_style.toolbar_button_hover_style if self.current_italic 
                    else toolbar_style.toolbar_button_style
                )

            print(f"Italic toggled: {self.current_italic}")

        except Exception as e:
            logger.error(f"Failed to toggle italic: {e}")
            QMessageBox.critical(self, "Error", f"Failed to toggle italic: {e}")









    def toggle_bold(self):
        """Toggle bold formatting while preserving the original font sizes and text colors."""
        try:
            cursor = self.text_edit.textCursor()

            # 1) No selection => Toggle the currentCharFormat only
            if not cursor.hasSelection():
                current_fmt = self.text_edit.currentCharFormat()
                is_bold = current_fmt.font().bold()
                new_bold_state = not is_bold
                current_fmt.setFontWeight(QFont.Bold if new_bold_state else QFont.Normal)
                self.text_edit.setCurrentCharFormat(current_fmt)
                self.current_bold = new_bold_state

            # 2) Selection => Check if entire selection is bold or not
            else:
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                temp_cursor = self.text_edit.textCursor()
                temp_cursor.setPosition(start)
                temp_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)

                # Check if all characters match the bold state of the first character
                first_char_bold = temp_cursor.charFormat().font().bold()
                all_same = True
                while temp_cursor.position() < end:
                    temp_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                    if temp_cursor.charFormat().font().bold() != first_char_bold:
                        all_same = False
                        break

                # If entire selection is uniformly bold => unbold it, else make it bold
                new_bold_state = not first_char_bold
                fmt = QTextCharFormat()
                fmt.setFontWeight(QFont.Bold if new_bold_state else QFont.Normal)
                cursor.mergeCharFormat(fmt)
                self.text_edit.setTextCursor(cursor)
                self.current_bold = new_bold_state

            # Update the bold button, if present
            if hasattr(self, "bold_button"):
                self.bold_button.setChecked(self.current_bold)
                # (Optional) update button stylesheet here

            print(f"Bold toggled: {self.current_bold}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to toggle bold: {e}")





    def select_highlight_color(self):
        """Toggle highlight formatting while keeping other styles intact, ensuring font size is preserved."""
        logger.info("Toggling Highlight")
        try:
            cursor = self.text_edit.textCursor()

            # 1) No selection => Toggle the highlight in currentCharFormat only
            if not cursor.hasSelection():
                current_fmt = self.text_edit.currentCharFormat()
                is_highlighted = (current_fmt.background().color() == QColor("#ffff00"))
                new_highlight_state = not is_highlighted
                new_bg = QColor("#ffff00") if new_highlight_state else QColor("white")
                current_fmt.setBackground(new_bg)
                self.text_edit.setCurrentCharFormat(current_fmt)

                # Update highlight button if present
                if hasattr(self, "highlight_button"):
                    self.highlight_button.setChecked(new_highlight_state)
                    self.highlight_button.setStyleSheet(
                        toolbar_style.toolbar_button_hover_style if new_highlight_state
                        else toolbar_style.toolbar_button_style
                    )
                    self.highlight_button.repaint()

            # 2) Selection => Check if the entire selection is uniformly highlighted
            else:
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                temp_cursor = self.text_edit.textCursor()
                temp_cursor.setPosition(start)
                temp_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)

                # Check if all characters match the highlight state of the first character
                first_bg = temp_cursor.charFormat().background().color()
                all_same = True
                while temp_cursor.position() < end:
                    temp_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                    if temp_cursor.charFormat().background().color() != first_bg:
                        all_same = False
                        break

                # If entire selection is uniformly highlighted => unhighlight, else highlight
                is_highlighted = (first_bg == QColor("#ffff00"))
                new_highlight_state = not is_highlighted
                new_bg = QColor("#ffff00") if new_highlight_state else QColor("white")

                # Check for mixed font sizes
                mixed_font_sizes = False
                temp_cursor.setPosition(start)  # Reset to start of selection
                first_size = temp_cursor.charFormat().fontPointSize()
                while temp_cursor.position() < end:
                    temp_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                    if temp_cursor.charFormat().fontPointSize() != first_size:
                        mixed_font_sizes = True
                        break

                fmt = QTextCharFormat()
                if not mixed_font_sizes:
                    # Preserve font size if uniform
                    current_format = cursor.charFormat()
                    font_size = current_format.fontPointSize() if current_format.fontPointSize() > 0 else self.current_font_size
                    fmt.setFontPointSize(font_size)
                    logger.info(f"Font size preserved: {font_size}")
                else:
                    logger.info("Mixed font sizes detected; preserving individual sizes by not overriding font size.")

                fmt.setBackground(new_bg)
                cursor.mergeCharFormat(fmt)
                self.text_edit.setTextCursor(cursor)

                # Update highlight button if present
                if hasattr(self, "highlight_button"):
                    self.highlight_button.setChecked(new_highlight_state)
                    self.highlight_button.setStyleSheet(
                        toolbar_style.toolbar_button_hover_style if new_highlight_state
                        else toolbar_style.toolbar_button_style
                    )
                    self.highlight_button.repaint()

            # Refresh the toolbar state
            self.update_toolbar_state()

        except Exception as e:
            logger.error(f"Failed to toggle highlight: {e}")
            QMessageBox.critical(self, "Error", f"Failed to toggle highlight: {e}")



    def submit_changes(self, file_path="report.html"):
        logger.info("Saves in html format")
        try:
            file_path = self.htmlfilepath
            html_content = self.text_edit.toHtml()
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):  # Check if directory exists
                os.makedirs(directory)
                
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(html_content)  # Write content safely
            self.save_to_database(html_content)  # Save to DB
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save HTML report: {e}")

    def add_row_below(self, cursor):
        table = cursor.currentTable()
        if table:
            current_row = cursor.currentTable().cellAt(cursor).row()
            table.insertRows(current_row + 1, 1)
             
    def add_row_above(self, cursor):
        table = cursor.currentTable()
        if table:
            current_row = cursor.currentTable().cellAt(cursor).row()
            table.insertRows(current_row , 1)        
      
    def delete_row(self, cursor):
        table = cursor.currentTable()
        if table and table.rows() > 1:
            current_row = cursor.currentTable().cellAt(cursor).row()
            table.removeRows(current_row, 1)
       
    def add_column_right(self, cursor):
        table = cursor.currentTable()
        if table:
            current_column = cursor.currentTable().cellAt(cursor).column()
            table.insertColumns(current_column + 1, 1)
        
    def add_column_left(self, cursor):
        table = cursor.currentTable()
        if table:
            current_column = cursor.currentTable().cellAt(cursor).column()
            table.insertColumns(current_column , 1)
       
    def delete_column(self, cursor):
        table = cursor.currentTable()
        if table and table.columns() > 1:
            current_column = cursor.currentTable().cellAt(cursor).column()
            table.removeColumns(current_column, 1)
    
    def insert_table(self):
        """Prompt the user for rows and columns and insert a table."""
        try:
            dialog = TableDialog(None)
            if dialog.exec_() == QDialog.Accepted:
                rows, columns = dialog.get_table_size()
                self.create_table(rows, columns)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to insert table: {e}")
        
    def create_table(self, rows, columns):
        """Create and insert a table with the specified rows and columns, ensuring correct font."""
        try:
            cursor = self.text_edit.textCursor()

            # Preserve current alignment before inserting the table
            current_paragraph_format = cursor.blockFormat()
            current_alignment = current_paragraph_format.alignment()

            # Define table format
            table_format = QTextTableFormat()
            table_format.setBorder(1)
            table_format.setCellPadding(5)
            table_format.setCellSpacing(0)

            # ✅ Insert the table
            table = cursor.insertTable(rows, columns, table_format)

            # ✅ Apply default text format inside each table cell
            fmt = QTextCharFormat()
            fmt.setFontPointSize(8)  # ✅ Force font size 8px
            fmt.setFontFamily("Arial")  # ✅ Ensure Arial font
            fmt.setForeground(QColor("black"))  # ✅ Ensure black text
            fmt.setBackground(QColor("white"))  # ✅ Ensure white background

            for row in range(rows):
                for col in range(columns):
                    cell = table.cellAt(row, col)
                    cell_cursor = cell.firstCursorPosition()
                    cell_cursor.mergeCharFormat(fmt)  # ✅ Apply 8px Arial inside each cell

            # ✅ Restore paragraph alignment after table insertion
            cursor.insertBlock()
            block_format = cursor.blockFormat()
            block_format.setAlignment(current_alignment)
            cursor.setBlockFormat(block_format)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create table: {e}")

    def show_numbering_menu(self):
        """Show a menu to select numbering styles, ensuring it opens below the button."""
        logger.info("Show Numbering Menu")
        try:
            menu = QMenu(self)
            menu.setStyleSheet("color: black")
            numbering_styles = [
                "1. Number Style 1",
                "A. Number Style 2",
                "i. Number Style 3",
            ]

            for style in numbering_styles:
                action = QAction(style, self)
                action.triggered.connect(
                    partial(self.apply_numbering_style, style)
                )  # Fix function scope issue
                menu.addAction(action)

            # Ensure the menu opens BELOW the icon
            menu.popup(
                self.numeric_button.mapToGlobal(self.numeric_button.rect().bottomLeft())
            )
           
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show numbering menu: {e}")

    def change_font(self):
        """Change the font style to Normal or Heading based on the combo box selection."""
        logger.info("Changing font style")

        try:
            if not hasattr(self, "text_edit") or not hasattr(self, "font_combo"):
                print("❌ Error: `text_edit` or `font_combo` not found")
                return
            
            if not hasattr(self, "font_combo") or not isinstance(self.font_combo, QComboBox):
                print(f"❌ Error: `font_combo` is not initialized as QComboBox, it is {type(self.font_combo)}")
                return

            cursor = self.text_edit.textCursor()
            fmt = QTextCharFormat()

            # Get selected font style from the combo box
            font_type = self.font_combo.currentText()

            if font_type == "Normal":
                fmt.setFontWeight(QFont.Normal)
                fmt.setFontPointSize(8)  #  Default normal text size
            elif font_type == "Heading":
                fmt.setFontWeight(QFont.Bold)
                fmt.setFontPointSize(16)  #  Larger font for heading

            #  Apply font style to selected text
            if cursor.hasSelection():
                cursor.mergeCharFormat(fmt)
            else:
                self.text_edit.setCurrentCharFormat(fmt)  #  Apply for new text

            #  Ensure toolbar reflects changes immediately
            self.update_toolbar_state()

            print(f" Changed font style to: {font_type}")
        
        except Exception as e:
            print(f"❌ Failed to change font: {e}")
            QMessageBox.critical(self, "Error", f"Failed to change font: {e}")

    def change_font_size(self):
        """
        Change the font size of the selected text while preserving bold, italic,
        highlight, and text color—even if different parts of the selection have
        different formatting.
        """
        logger.info("Change font size")
        try:
            if not hasattr(self, "font_size_combo"):
                QMessageBox.warning(self, "Error", "Font size selector not found.")
                return

            selected_size = int(self.font_size_combo.currentText())
            self.current_font_size = selected_size  # Store size for new text

            cursor = self.text_edit.textCursor()

            if cursor.hasSelection():
                # 1) Character-by-character approach to preserve ALL mixed formatting
                start = cursor.selectionStart()
                end = cursor.selectionEnd()

                # We'll use a separate cursor that we move through each character
                temp_cursor = QTextCursor(self.text_edit.document())
                temp_cursor.setPosition(start)

                # Begin edit block for efficiency
                cursor.beginEditBlock()

                # Loop over each character in the selection
                while temp_cursor.position() < end:
                    # Select one character
                    temp_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                    # Copy its current format
                    char_format = temp_cursor.charFormat()
                    new_format = QTextCharFormat(char_format)
                    # Only update the font size
                    new_format.setFontPointSize(selected_size)
                    # Merge back
                    temp_cursor.mergeCharFormat(new_format)

                    # Move to the next character (no selection)
                    temp_cursor.setPosition(temp_cursor.position(), QTextCursor.MoveAnchor)

                cursor.endEditBlock()

                # Restore user selection
                # (Re-select the original range so the user still sees the selection)
                cursor.setPosition(start, QTextCursor.MoveAnchor)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                self.text_edit.setTextCursor(cursor)

                print(f"🎯 Font size changed for selection to: {selected_size}")
            else:
                # 2) No selection => Update the default format for future typing
                current_format = self.text_edit.currentCharFormat()
                new_format = QTextCharFormat(current_format)
                new_format.setFontPointSize(selected_size)
                self.text_edit.setCurrentCharFormat(new_format)
                print(f"🎯 Default font size set for future text: {selected_size}")

            logger.info(f"Font size updated to {selected_size}")

            # Update the font-size combo box to reflect the new font size
            if hasattr(self, "font_size_combo"):
                self.font_size_combo.blockSignals(True)
                self.font_size_combo.setCurrentText(str(int(self.current_font_size)))
                self.font_size_combo.blockSignals(False)

        except ValueError:
            QMessageBox.warning(self, "Invalid Font Size", "Please select a valid font size.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to change font size: {e}")



    def apply_current_font(self, attribute):
        """Apply the current font, size, and styles to selected text without unwanted resets."""
        logger.info("Apply Current font")

        try:
            cursor = self.text_edit.textCursor()
            if not cursor.isNull():
                fmt = QTextCharFormat()  # Start with a clean format

                #  Preserve Font Family
                if (
                    hasattr(self, "current_font")
                    and self.current_font
                    and (attribute == "setfont")
                ):
                    fmt.setFont(self.current_font)
                    logger.info(f"Font applied: {self.current_font.family()}")

                #  Preserve Font Size
                if (
                    hasattr(self, "current_font_size")
                    and self.current_font_size
                    and (attribute == "setfontpointsize")
                ):
                    fmt.setFontPointSize(self.current_font_size)
                    logger.info(f"Font Size applied: {self.current_font_size}")

                #  Preserve Font Color
                if (
                    hasattr(self, "current_font_color")
                    and self.current_font_color
                    and (attribute == "setfontcolor")
                ):
                    fmt.setForeground(self.current_font_color)
                    logger.info(f"Font Color applied: {self.current_font_color.name()}")

                #  Preserve Highlight Color
                if (
                    hasattr(self, "current_highlight_color")
                    and self.current_highlight_color
                    and (attribute == "setbackground")
                ):
                    fmt.setBackground(self.current_highlight_color)
                    logger.info(
                        f"Highlight applied: {self.current_highlight_color.name()}"
                    )

                #  Preserve Bold, Italic, and Underline
                if (
                    hasattr(self, "current_bold")
                    and self.current_bold
                    and (attribute == "setfontweight")
                ):
                    fmt.setFontWeight(QFont.Bold)
                    logger.info("Bold applied")
                else:
                    fmt.setFontWeight(QFont.Normal)

                if (
                    hasattr(self, "current_italic")
                    and self.current_italic
                    and (attribute == "setfontitalic")
                ):
                    fmt.setFontItalic(True)
                    logger.info("Italic applied")
                else:
                    fmt.setFontItalic(False)

                if (
                    hasattr(self, "current_underline")
                    and self.current_underline
                    and (attribute == "setfontunderline")
                ):
                    fmt.setFontUnderline(True)
                    logger.info("Underline applied")
                else:
                    fmt.setFontUnderline(False)

                #  Merge format without overriding user-set styles
                cursor.mergeCharFormat(fmt)
                self.text_edit.setTextCursor(cursor)

                print(" Formatting applied successfully")

            else:
                logger.warning("No valid text selection found.")
            
        except Exception as e:
            logger.error(f"Failed to apply font settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to apply font settings: {e}")

    def select_font_color(self):
        """Open a color dialog to select the font color while preserving existing formatting."""
        logger.info("Selecting font color")

        try:
            default_color = QColor("grey")  # Default color
            color = QColorDialog.getColor(default_color, self)

            if color.isValid():
                cursor = self.text_edit.textCursor()
                fmt = QTextCharFormat()

                if cursor.hasSelection():
                    # 1) If there is a selection, apply ONLY the color.
                    fmt.setForeground(color)
                    cursor.mergeCharFormat(fmt)
                    self.text_edit.setTextCursor(cursor)
                else:
                    # 2) No selection => update the current typing format,
                    #    preserving the existing font size from currentCharFormat.
                    current_fmt = self.text_edit.currentCharFormat()
                    existing_size = current_fmt.fontPointSize()
                    
                    # Only set the color; keep the existing size if it's valid.
                    if existing_size > 0:
                        fmt.setFontPointSize(existing_size)
                    
                    fmt.setForeground(color)
                    self.text_edit.setCurrentCharFormat(fmt)

                # Update our stored current_font_color if you track it
                self.current_font_color = color

                logger.info(f"Font color changed to {color.name()}, preserving other attributes.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to select font color: {e}")




    def change_alignment(self, alignment, table=None):
        """Change the alignment of the selected text or specific table cell and update the alignment icon."""
        logger.info("Changing Alignment")

        try:
            cursor = self.text_edit.textCursor()

            if table is None:
                table = cursor.currentTable()

            if table:
                # ✅ Apply alignment only to the selected cell(s)
                selected_cells = []
                for row in range(table.rows()):
                    for col in range(table.columns()):
                        cell = table.cellAt(row, col)
                        if cell.isValid():
                            cell_cursor = cell.firstCursorPosition()
                            if cursor.selectionStart() <= cell_cursor.position() <= cursor.selectionEnd():
                                selected_cells.append(cell)

                if selected_cells:
                    for cell in selected_cells:
                        cell_cursor = cell.firstCursorPosition()
                        block_format = QTextBlockFormat()
                        block_format.setAlignment(alignment)
                        cell_cursor.mergeBlockFormat(block_format)
                    print(f"✅ Alignment applied to selected cell(s): {alignment}")
                else:
                    print("⚠️ No specific table cell detected, applying to whole table.")

            else:
                # ✅ Apply alignment to normal text (outside table)
                block_format = QTextBlockFormat()
                block_format.setAlignment(alignment)

                if alignment == "justify":
                    block_format.setAlignment(Qt.AlignJustify)
                else:
                    block_format.setAlignment(alignment)

                cursor.mergeBlockFormat(block_format)
                self.text_edit.setTextCursor(cursor)
                print(f"✅ Alignment applied to selected text: {alignment}")

            # ✅ Force toolbar state update
            self.update_toolbar_state()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to change alignment: {e}")

    def insert_picture(self):
        """Prompt the user for image dimensions before inserting it into QTextEdit."""
        try:
            project_path = P.project_path  # Access project path directly

            if not project_path:
                QMessageBox.warning(self, "Error", "Project path is not set. Open a project first.")
                return

            # Define image folder inside the project path
            image_folder = os.path.join(project_path, "descriptionimage")

            # Create folder if it doesn't exist
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)

            # Open file dialog to select an image
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "",
                                                    "Images (*.png *.jpg *.bmp);;All Files (*)")

            if not file_name:
                return  # No file selected

            # Load the image to get original dimensions
            image = QImage(file_name)
            if image.isNull():
                QMessageBox.warning(self, "Error", "Invalid image file. Please select a valid image.")
                return
            
            original_width = image.width()
            original_height = image.height()

            # Ask user for width
            width, ok_w = QInputDialog.getInt(None, "Image Width", "Enter width:",
                                            original_width, 50, 2000)
            if not ok_w:
                return  

            # Ask user for height
            height, ok_h = QInputDialog.getInt(None, "Image Height", "Enter height:",
                                            original_height, 50, 2000)
            if not ok_h:
                return  

            # Save image inside the folder
            image_path = os.path.join(image_folder, os.path.basename(file_name))
            pixmap = QPixmap(file_name)
            success = pixmap.save(image_path, "PNG")  # Always save as PNG

            if success:
                print(f"✅ Image successfully saved at: {image_path}")
            else:
                print(f"❌ Failed to save image at: {image_path}")

            # Check if file exists after saving
            if not os.path.exists(image_path):
                QMessageBox.critical(self, "Error", "Image was not saved correctly.")
                return

            # ✅ Insert a newline before the image to ensure it appears on a new line
            cursor = self.text_edit.textCursor()
            cursor.movePosition(QTextCursor.End)  # Move to the end of text
            cursor.insertBlock()  # Insert a new paragraph before the image

            # Insert image with specified dimensions
            image_html = f'<img src="{image_path}" width="{width}" height="{height}">'
            cursor.insertHtml(image_html)

            # ✅ Insert another newline after the image to avoid text sticking to it
            cursor.insertBlock()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inserting image: {e}")
            print(f"❌ Exception occurred: {e}")

    def load_saved_images(self):
        try:
            project_path = P.project_path  # Access project path directly
 
            if not project_path:
                return  # No project path set
 
            image_folder = os.path.join(project_path, "descriptionimage")
 
            if not os.path.exists(image_folder):
                return  # Folder doesn't exist, so no images to load
 
            # Iterate through images and insert them into QTextEdit
            for img_file in os.listdir(image_folder):
                if img_file.endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    img_path = os.path.join(image_folder, img_file)
                    image_html = f'<img src="{img_path}" width="200">'
                    self.text_edit.insertHtml(image_html)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading saved images: {e}")
    
    def show_bullet_menu(self):
        """Show a menu to select bullet styles."""
        logger.info("Show Bullet Menu")
        try:
            menu = QMenu(self)
            menu.setStyleSheet("color: black")
            bullet_styles = ["• Bullet Style 1", "◦ Bullet Style 2", "▪ Bullet Style 3"]

            for style in bullet_styles:
                action = QAction(style, self)
                action.triggered.connect(
                    partial(self.apply_bullet_style, style)
                )  #  Fix incorrect lambda referencing
                menu.addAction(action)

            menu.exec_(self.cursor().pos())
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show bullet menu: {e}")

    def apply_bullet_style(self, style):
        """Toggle bullet points on selected text smoothly, allowing direct switching between styles."""
        logger.info("Apply Bullet Style")

        try:
            cursor = self.text_edit.textCursor()
            if cursor.isNull():
                return

            block = cursor.block()
            list_format = block.textList()
            current_list = None

            # ✅ Detect current bullet style
            if list_format:
                current_list = list_format.format().style()

            # ✅ Map bullet styles to corresponding QTextListFormat values
            bullet_styles = {
                "• Bullet Style 1": QTextListFormat.ListDisc,
                "◦ Bullet Style 2": QTextListFormat.ListCircle,
                "▪ Bullet Style 3": QTextListFormat.ListSquare,
            }
            new_style = bullet_styles.get(style)

            # ✅ If the same bullet is clicked, remove bullets and clear indentation
            if current_list == new_style:
                cursor.beginEditBlock()  # ✅ Start edit block to ensure changes are tracked
                
                # ✅ Remove list by clearing list format for each block
                while block.isValid() and block.textList():
                    block_list = block.textList()
                    block_list.remove(block)
                    block = block.next()

                self.remove_indent(cursor)  # ✅ Clear tab space after bullet removal
                cursor.endEditBlock()

                self.current_list_format = None
                logger.info("🚀 Bullets removed, indentation cleared")

            else:
                # ✅ Apply the selected bullet style without removing existing bullets first
                list_format = QTextListFormat()
                list_format.setStyle(new_style)

                # ✅ Maintain indentation but prevent excessive indentation
                indent_value = max(1, min(4, int(self.current_font_size / 10)))
                list_format.setIndent(indent_value)

                cursor.createList(list_format)
                self.current_list_format = "bullets"
                logger.info(f"✅ Bullet style switched to {style}")

            self.text_edit.setTextCursor(cursor)
            self.update_toolbar_state()  # ✅ Ensure UI updates immediately

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply bullet style: {e}")
    
    def apply_numbering_style(self, style):
        """Toggle numbering on selected text smoothly, allowing direct switching between styles."""
        logger.info("Apply Numbering Style")

        try:
            cursor = self.text_edit.textCursor()
            if cursor.isNull():
                return

            block = cursor.block()
            list_format = block.textList()
            current_list = None

            # ✅ Detect current numbering style
            if list_format:
                current_list = list_format.format().style()

            # ✅ Map numbering styles to corresponding QTextListFormat values
            numbering_styles = {
                "1. Number Style 1": QTextListFormat.ListDecimal,
                "A. Number Style 2": QTextListFormat.ListUpperAlpha,
                "i. Number Style 3": QTextListFormat.ListLowerRoman,
            }
            new_style = numbering_styles.get(style)

            # ✅ If the same numbering style is clicked, remove numbering and clear indentation
            if current_list == new_style:
                cursor.beginEditBlock()  # ✅ Start edit block to ensure changes are tracked
                
                # ✅ Remove numbering by clearing list format for each block
                while block.isValid() and block.textList():
                    block_list = block.textList()
                    block_list.remove(block)
                    block = block.next()

                self.remove_indent(cursor)  # ✅ Clear tab space after numbering removal
                cursor.endEditBlock()

                self.current_list_format = None
                logger.info("🚀 Numbering removed, indentation cleared")

            else:
                # ✅ Apply the selected numbering style without removing existing numbering first
                list_format = QTextListFormat()
                list_format.setStyle(new_style)

                # ✅ Maintain indentation but prevent excessive indentation
                indent_value = max(1, min(5, int(self.current_font_size / 10)))
                list_format.setIndent(indent_value)

                cursor.createList(list_format)
                self.current_list_format = "numbering"
                logger.info(f"✅ Numbering style switched to {style}")

            self.text_edit.setTextCursor(cursor)
            self.update_toolbar_state()  # ✅ Ensure UI updates immediately

        except Exception as e:
            logger.error(f"Failed to apply numbering style: {e}")
            QMessageBox.critical(self, "Error", f"Failed to apply numbering style: {e}")

    def remove_indent(self, cursor):
        """Remove indentation from the selected paragraph when bullets are removed."""
        block_format = cursor.blockFormat()
        block_format.setIndent(0)  # ✅ Reset indentation
        cursor.mergeBlockFormat(block_format)

    def save_to_database(self, html_content):
        """Save the HTML content into a database."""
        try:
            if not html_content:  # ✅ Ensure content is valid
                logger.warning("❗ No HTML content provided for saving.")
                interfaces.unsaved_changes = False
                return

            print("\n📝 **Saving Content to Database:**\n", html_content, "\n---\n")  # ✅ Print saved content

            DB.update_db("""INSERT OR REPLACE INTO MS_Description (id, content) VALUES (1, ?);""", (html_content,))
            interfaces.unsaved_changes = False
            # QMessageBox.information(None, "Success", "Data saved to the database successfully.")
        except Exception as e:
            logger.error(f"Failed to save data to the database: {e}")
            QMessageBox.critical(
                self, "Error", f"Failed to save data to the database: {e}"
            )


    def load_from_database(self, record_id):
        """Retrieve HTML content from the database and display it in QTextEdit."""
        try:
            
            result = DB.execute_db(f""" SELECT content FROM MS_Description WHERE id = {record_id}""")
            
            if result and result[0][0]:  # Ensure result is not empty
                html_content = result[0][0]
                print("\n📜 **Loaded Content from Database:**\n", html_content, "\n---\n")  # ✅ Print loaded content
                self.text_edit.setHtml(html_content)
            else:
                self.text_edit.clear()
            interfaces.unsaved_changes = False    
        except Exception as e:
            QMessageBox.critical(
                self, "Database Error", f"Failed to load data from the database: {e}"
            )
    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True 
class TableDialog(QDialog):
    """Dialog to get the number of rows and columns for table creation."""

    def __init__(self, parent=None):
        logger.info("Table creation")
        super().__init__(parent)
        self.setWindowTitle("Insert Table")
        self.setFixedSize(300, 150)

        layout = QGridLayout()
        self.setStyleSheet("color: black")

        # Label and SpinBox for rows
        layout.addWidget(QLabel("Number of Rows:"), 0, 0)
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setMinimum(1)
        self.rows_spinbox.setMaximum(100)
        layout.addWidget(self.rows_spinbox, 0, 1)

        # Label and SpinBox for columns
        layout.addWidget(QLabel("Number of Columns:"), 1, 0)
        self.columns_spinbox = QSpinBox()
        self.columns_spinbox.setMinimum(1)
        self.columns_spinbox.setMaximum(20)
        layout.addWidget(self.columns_spinbox, 1, 1)
        
        # ✅ Ensure every cell inherits the default font settings
        fmt = QTextCharFormat()
        fmt.setFontPointSize(8)  # Force default font size
        fmt.setFontFamily("Arial")  # Ensure consistent font family

        # Insert and Cancel buttons
        self.insert_button = QPushButton("Insert Table")
        self.insert_button.clicked.connect(self.accept)
        layout.addWidget(self.insert_button, 2, 0)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button, 2, 1)

        self.setLayout(layout)

    def get_table_size(self):
        """Return the selected number of rows and columns."""
        return self.rows_spinbox.value(), self.columns_spinbox.value()
    

class CleanTextEdit(QTextEdit):
    def insertFromMimeData(self, source):
        # Handle pasted images first
        if source.hasImage():
            image = source.imageData()
            if image:
                image_name = "pasted_image.png"
                self.document().addResource(QTextDocument.ImageResource, QUrl(image_name), image)
                self.textCursor().insertHtml(f'<img src="{image_name}">')
                return

        # Clean up any HTML — strip inline font-size/family
        if source.hasHtml():
            html = source.html()
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all():
                if tag.has_attr("style"):
                    styles = [
                        s.strip() for s in tag["style"].split(";")
                        if s.strip() and not s.strip().startswith(("font-size", "font-family"))
                    ]
                    tag["style"] = "; ".join(styles)
            self.insertHtml(str(soup))
            return

        # Fallback for plain text
        super(CleanTextEdit, self).insertFromMimeData(source)
