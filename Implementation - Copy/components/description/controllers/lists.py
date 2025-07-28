# File: components/description/controllers/lists.py
"""
Module: List Controller
File: lists.py
Layer: UI / Controller Layer
Component ID: 
Requirement IDs: 
Author: Vijaya Ragavan
Created On: 2025-06-27
Version: 

Purpose:
--------
Provides `ListController`, which toggles bulleted and numbered lists
in a `QTextEdit`, matching legacy Scope Description behavior.

Responsibilities:
-----------------
• Listen for bullets/numbering signals from the toolbar.  
• Determine whether to wrap selection in a list or unwrap it.  
• Support single‑block and multi‑block selections.  
• Maintain user’s indentation levels when unwrapping lists.  

Public API:
-----------
class ListController:
  __init__(text_edit: QTextEdit, toolbar) -> None  
    • Connects `toolbar.bulletsClicked` to `toggle_bullets`.  
    • Connects `toolbar.numberingClicked` to `toggle_numbering`.  

  toggle_bullets() -> None  
    • Toggles a disc‑style list on the current selection or block.  

  toggle_numbering() -> None  
    • Toggles a decimal‑style list on the current selection or block.  
"""
# pylint: disable=E0611

import logging
from typing import List
from PyQt5.QtGui import QTextListFormat, QTextCursor, QTextBlock
from PyQt5.QtWidgets import QTextEdit

logger = logging.getLogger(__name__)

class ListController:
    """
    Handles bullet and numbering list insertion and toggling.
    """

    def __init__(self, text_edit: QTextEdit, toolbar) -> None:
        """
        Connect toolbar signals (or callable stubs) to list toggles.

        Args:
            text_edit: The QTextEdit instance in which to toggle lists.
            toolbar:   The toolbar emitting bulletsClicked/numberingClicked.
        """
        self.text_edit = text_edit

        sig1 = getattr(toolbar, "bulletsClicked", None)
        if hasattr(sig1, "connect"):
            sig1.connect(self.toggle_bullets)
        elif callable(sig1):
            sig1(self.toggle_bullets)

        sig2 = getattr(toolbar, "numberingClicked", None)
        if hasattr(sig2, "connect"):
            sig2.connect(self.toggle_numbering)
        elif callable(sig2):
            sig2(self.toggle_numbering)

    def toggle_bullets(self) -> None:
        """Toggle a bulleted (disc) list on the current selection or block."""
        self._toggle_list(QTextListFormat.ListDisc)

    def toggle_numbering(self) -> None:
        """Toggle a numbered (decimal) list on the current selection or block."""
        self._toggle_list(QTextListFormat.ListDecimal)

    def _toggle_list(self, style: QTextListFormat.Style) -> None:
        """
        Apply or remove a list of the given style.

        If every block in the current selection is already in a list of this style,
        unwraps those blocks back into normal paragraphs. Otherwise, wraps them
        in a new list at indent level 1.
        """
        cursor = self.text_edit.textCursor()
        blocks = self._blocks_in_selection(cursor)

        all_same = all(
            block.textList() is not None and
            block.textList().format().style() == style
            for block in blocks
        )

        cursor.beginEditBlock()
        if all_same:
            for block in blocks:
                lst = block.textList()
                if lst:
                    lst.remove(block)
                fmt = block.blockFormat()
                fmt.setIndent(0)
                temp = QTextCursor(block)
                temp.setBlockFormat(fmt)
            logger.info("Removed list formatting from %d blocks", len(blocks))
        else:
            fmt = QTextListFormat()
            fmt.setStyle(style)
            fmt.setIndent(1)
            cursor.createList(fmt)
            logger.info("Applied list style %r to selection", style)
        cursor.endEditBlock()

    def _blocks_in_selection(self, cursor: QTextCursor) -> List[QTextBlock]:
        """
        Collect all QTextBlock objects in the current selection.

        If there is no selection, returns the single block containing the cursor.
        """
        doc = self.text_edit.document()
        if cursor.hasSelection():
            start, end = cursor.selectionStart(), cursor.selectionEnd()
            block = doc.findBlock(start)
            result: List[QTextBlock] = []
            while block.isValid() and block.position() < end:
                result.append(block)
                block = block.next()
            return result
        return [cursor.block()]
