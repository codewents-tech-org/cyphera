# pylint: disable=E0611,E0401,W0718,R0903,C0301,C0303
"""
Module: Alignment Controller
File: alignment.py
Layer: UI / Controller Layer
Component ID: 
Requirement IDs: 
Author: Vijaya Ragaavan
Created On: 2025-06-27
Version: .0

Purpose:
--------
Provides `AlignmentController`, which applies paragraph and table-cell
alignment to a QTextEdit per legacy Scope Description requirements.

Responsibilities:
-----------------
• Listen for `alignChanged` signals.  
• Iterate selected text blocks and tables.  
• Apply alignment to paragraphs or whole/partial tables.  
• Restore the original selection.  
• Return success status and log errors.
"""

import logging
from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QTextBlockFormat

logger = logging.getLogger(__name__)


class AlignmentController:
    """
    Handles paragraph and table-cell alignment for a QTextEdit.
    """
    def __init__(self, text_edit, toolbar) -> None:
        """
        Args:
            text_edit: The QTextEdit instance.
            toolbar:   Emits `alignChanged` signals.
        """
        self.text_edit = text_edit
        toolbar.alignChanged.connect(self.change_alignment)

    def change_alignment(self, alignment: Union[Qt.AlignmentFlag, int]) -> bool:
        """
        Apply the given alignment to the current selection.

        Args:
            alignment: Qt.AlignLeft/Center/Right/Justify or raw int.

        Returns:
            True if applied successfully; False otherwise.
        """
        logger.debug("change_alignment called with alignment=%r", alignment)

        # Normalize and validate only the four supported modes
        try:
            if not isinstance(alignment, Qt.AlignmentFlag):
                alignment = Qt.Alignment(alignment)
        except Exception:
            logger.error("Invalid alignment argument: %r", alignment)
            return False

        if alignment not in {
            Qt.AlignLeft,
            Qt.AlignCenter,
            Qt.AlignRight,
            Qt.AlignJustify,
        }:
            logger.error("Unsupported alignment mode: %r", alignment)
            return False

        try:
            cursor = self.text_edit.textCursor()
            doc = self.text_edit.document()
            start = cursor.selectionStart()
            end = cursor.selectionEnd()

            applied_to_text = False
            processed_tables = set()
            block = doc.findBlock(start)

            while block.isValid() and block.position() <= end:
                temp = QTextCursor(block)
                table = temp.currentTable()

                if table:
                    tid = id(table)
                    if tid not in processed_tables:
                        self._align_table_or_cells(
                            table, start, end, alignment
                        )
                        processed_tables.add(tid)
                else:
                    fmt = QTextBlockFormat()
                    fmt.setAlignment(alignment)
                    temp.mergeBlockFormat(fmt)
                    applied_to_text = True
                    logger.debug(
                        "Aligned paragraph at pos %d", block.position()
                    )

                block = block.next()

            # Restore selection
            self.text_edit.setTextCursor(cursor)
            if applied_to_text:
                logger.info("Aligned plain text blocks in selection")
            return True

        except Exception as e:
            logger.error("Failed to change alignment: %s", e)
            return False

    def _align_table_or_cells(
        self,
        table,
        start: int,
        end: int,
        alignment: Union[Qt.AlignmentFlag, int],
    ) -> None:
        """
        Align a whole table or selected cells.

        Args:
            table:     The QTextTable to modify.
            start:     Selection start position.
            end:       Selection end position.
            alignment: Alignment flag.
        """
        first = table.cellAt(0, 0).firstCursorPosition().position()
        last = (
            table.cellAt(table.rows() - 1, table.columns() - 1)
            .lastCursorPosition()
            .position()
        )

        if start <= first and end >= last:
            fmt = table.format()
            fmt.setAlignment(alignment)
            table.setFormat(fmt)
            logger.info("Aligned entire table id=%s", id(table))
        else:
            cell_fmt = QTextBlockFormat()
            cell_fmt.setAlignment(alignment)
            for r in range(table.rows()):
                for c in range(table.columns()):
                    cell = table.cellAt(r, c)
                    pos = cell.firstCursorPosition().position()
                    if start <= pos <= end:
                        cur = cell.firstCursorPosition()
                        cur.mergeBlockFormat(cell_fmt)
                        logger.debug(
                            "Aligned cell(%d,%d) in table id=%s",
                            r,
                            c,
                            id(table),
                        )
            logger.info("Aligned selected cells in table id=%s", id(table))
