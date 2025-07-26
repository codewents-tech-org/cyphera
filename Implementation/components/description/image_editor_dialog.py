# pylint: disable=E0611,E0401,W0718
"""
Module: Resizable Image Dialog
File: image_editor_dialog.py
Layer: UI / Image Editing Layer
Component ID: CY_DE_003
Requirement IDs: DE-IMG-001, DE-IMG-002, DE-IMG-003
Author: Vijaya Karagi
Created On: 2025-06-26
Version: V1.2

Purpose:
--------
Provides `ResizableImageDialog`, a modal dialog that lets users
interactively resize an image via drag‐handles before inserting it
back into the editor.

Responsibilities:
-----------------
• Display the source image at full resolution.  
• Overlay eight draggable handles for corner/edge resizing.  
• Perform fast scaling during drag, smooth scaling on release.  
• Emit `image_edited` when “Apply & Insert” is clicked.  
• Return the final (path, width, height) via `get_resized_image()`.  

Public API:
-----------
class ResizeHandle(position: str, parent_item: QGraphicsPixmapItem, size: int = 8)
  • Drag handles for interactive resize; no public methods beyond inherited.

class ResizablePixmapItem(display_pixmap: QPixmap, original_pixmap: QPixmap)
  • resize_with_delta(handle: str, delta: QPointF) -> None  
  • finalize_resize() -> None  

class ResizableImageDialog(image_path: str, parent=None, base_image_path=None)
  • on_accept() -> None  
  • get_resized_image() -> Tuple[str, int, int]  

Signals:
--------
+---------------+--------------+--------------------------------------------+
| Signal        | Emitted on   | Payload                                    |
+===============+==============+============================================+
| image_edited  | on_accept()  | None; caller then calls `get_resized_image`|
+---------------+--------------+--------------------------------------------+
"""

import logging
import os
import uuid
from typing import Tuple, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsView, QGraphicsScene, QFrame, QLabel,
    QGraphicsPixmapItem, QGraphicsEllipseItem
)
from PyQt5.QtGui    import QPixmap, QBrush, QPen, QPainter
from PyQt5.QtCore   import Qt, QPointF, pyqtSignal

logger = logging.getLogger(__name__)


class ResizeHandle(QGraphicsEllipseItem):
    """
    A draggable ellipse grip for resizing a ResizablePixmapItem.
    """
    CURSORS = {
        'top-left': Qt.SizeFDiagCursor, 'bottom-right': Qt.SizeFDiagCursor,
        'top-right': Qt.SizeBDiagCursor, 'bottom-left': Qt.SizeBDiagCursor,
        'top': Qt.SizeVerCursor, 'bottom': Qt.SizeVerCursor,
        'left': Qt.SizeHorCursor, 'right': Qt.SizeHorCursor
    }

    def __init__(
        self,
        position: str,
        parent_item: QGraphicsPixmapItem,
        size: int = 8
    ) -> None:
        """
        Args:
            position: One of 'top-left', 'top', 'top-right', etc.
            parent_item: The ResizablePixmapItem this handle belongs to.
            size: Diameter of the handle circle.
        """
        super().__init__(-size/2, -size/2, size, size, parent_item)
        self.position = position
        self.setBrush(QBrush(Qt.white))
        self.setPen(QPen(Qt.black, 1))
        self.setCursor(self.CURSORS.get(position, Qt.ArrowCursor))
        self._press_scene_pos: Optional[QPointF] = None
        self._orig_size: Tuple[float, float] = (0.0, 0.0)
        self._orig_item_pos = QPointF(0.0, 0.0)

    def mousePressEvent(self, event) -> None:
        """
        Record initial pointer location and pixmap size.
        """
        parent = self.parentItem()
        self._press_scene_pos = event.scenePos()
        rect = parent.boundingRect()
        self._orig_size = (rect.width(), rect.height())
        self._orig_item_pos = parent.pos()
        event.accept()

    def mouseMoveEvent(self, event) -> None:
        """
        Resize the parent item as the handle is dragged.
        """
        parent = self.parentItem()
        delta = event.scenePos() - self._press_scene_pos
        parent.resize_with_delta(self.position, delta)
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        """
        Perform a final high-quality rescale on release.
        """
        parent = self.parentItem()
        parent.finalize_resize()
        event.accept()


class ResizablePixmapItem(QGraphicsPixmapItem):
    """
    A pixmap item with eight ResizeHandle grips for interactive resizing.
    """
    def __init__(self, display_pixmap: QPixmap, original_pixmap: QPixmap) -> None:
        """
        Args:
            display_pixmap: Pixmap used for fast, on-drag scaling.
            original_pixmap: Full-resolution source for smooth scaling.
        """
        super().__init__(display_pixmap)
        self._original_pixmap = original_pixmap
        self.setFlags(
            QGraphicsPixmapItem.ItemIsSelectable |
            QGraphicsPixmapItem.ItemIsMovable
        )
        self._ratio = (
            original_pixmap.width() / original_pixmap.height()
            if original_pixmap.height() else 1.0
        )
        self._orig_size = (
            display_pixmap.width(),
            display_pixmap.height()
        )
        self._orig_item_pos = QPointF(0.0, 0.0)

        # create and position the eight drag-handles
        self.handles = {
            pos: ResizeHandle(pos, self)
            for pos in [
                'top-left', 'top', 'top-right', 'right',
                'bottom-right', 'bottom', 'bottom-left', 'left'
            ]
        }
        self.update_handles()

    def update_handles(self) -> None:
        """
        Reposition handles around the current bounding box.
        """
        r = self.boundingRect()
        cx, cy = r.center().x(), r.center().y()
        coords = {
            'top-left':     QPointF(r.left(),  r.top()),
            'top':          QPointF(cx,        r.top()),
            'top-right':    QPointF(r.right(), r.top()),
            'right':        QPointF(r.right(), cy),
            'bottom-right': QPointF(r.right(), r.bottom()),
            'bottom':       QPointF(cx,        r.bottom()),
            'bottom-left':  QPointF(r.left(),  r.bottom()),
            'left':         QPointF(r.left(),  cy),
        }
        for name, pos in coords.items():
            self.handles[name].setPos(pos)

    def paint(self, painter: QPainter, option, widget) -> None:
        """
        Draw the pixmap; if selected, draw a dashed blue outline.
        """
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(QPen(Qt.blue, 1, Qt.DashLine))
            painter.drawRect(self.boundingRect())

    def resize_with_delta(self, handle: str, delta: QPointF) -> None:
        """
        Fast-scale the pixmap during drag, maintaining aspect on corners.

        Args:
            handle: Which grip is being dragged.
            delta: Movement since mouse down.
        """
        w0, h0 = self._orig_size
        ox, oy = self._orig_item_pos.x(), self._orig_item_pos.y()
        dw, dh = delta.x(), delta.y()
        new_w, new_h = w0, h0
        dx = dy = 0.0

        # compute new size & offset for each handle
        if handle == 'bottom-right':
            new_w, new_h = w0 + dw, h0 + dh
        elif handle == 'bottom-left':
            new_w, new_h = w0 - dw, h0 + dh; dx = dw
        elif handle == 'top-right':
            new_w, new_h = w0 + dw, h0 - dh; dy = dh
        elif handle == 'top-left':
            new_w, new_h = w0 - dw, h0 - dh; dx, dy = dw, dh
        elif handle == 'right':
            new_w = w0 + dw
        elif handle == 'left':
            new_w = w0 - dw; dx = dw
        elif handle == 'bottom':
            new_h = h0 + dh
        elif handle == 'top':
            new_h = h0 - dh; dy = dh
        else:
            return

        new_w, new_h = max(10, new_w), max(10, new_h)

        # lock aspect ratio on corner drags
        if handle in (
            'top-left', 'top-right', 'bottom-left', 'bottom-right'
        ):
            if abs(dw) > abs(dh):
                new_h = new_w / self._ratio
            else:
                new_w = new_h * self._ratio

        fast_pix = self._original_pixmap.scaled(
            int(new_w), int(new_h),
            Qt.KeepAspectRatio, Qt.FastTransformation
        )
        self.setPixmap(fast_pix)
        self.setPos(QPointF(ox + dx, oy + dy))
        self.update_handles()

    def finalize_resize(self) -> None:
        """
        On mouse release, perform a high‐quality smooth scaling.
        """
        size = self.boundingRect().size().toSize()
        smooth = self._original_pixmap.scaled(
            size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.setPixmap(smooth)
        self.update_handles()


class ResizableImageDialog(QDialog):
    """
    A modal dialog that lets users drag‐resize an image before inserting.
    """
    image_edited = pyqtSignal()

    def __init__(
        self,
        image_path: str,
        parent: Optional[QDialog] = None,
        base_image_path: Optional[str] = None
    ) -> None:
        """
        Args:
            image_path:         Path to the image to resize.
            parent:             Optional parent widget.
            base_image_path:    If set, use this for final high-res scaling.
        """
        super().__init__(parent)
        self.setWindowTitle("Resize & Insert Image")
        self.setModal(True)
        self.setMinimumSize(600, 400)

        self.base_image_path = base_image_path or image_path
        orig = QPixmap(self.base_image_path)
        display = orig.copy()

        self._setup_ui(display)
        self._load_pixmap(display)

    def _setup_ui(self, display: QPixmap) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        lbl = QLabel("Drag any handle to resize. Click “Apply & Insert” when done:")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setFrameShape(QFrame.Box)
        layout.addWidget(self.view, stretch=1)

        btn = QPushButton("Apply & Insert", self)
        btn.setFixedHeight(32)
        btn.clicked.connect(self.on_accept)
        layout.addWidget(btn)

    def _load_pixmap(self, display: QPixmap) -> None:
        """
        Add the ResizablePixmapItem to the QGraphicsScene.
        """
        orig = QPixmap(self.base_image_path)
        self.item = ResizablePixmapItem(display, orig)
        self.scene.clear()
        self.scene.addItem(self.item)
        self.view.setScene(self.scene)

    def on_accept(self) -> None:
        """
        Emit `image_edited` and close the dialog.
        """
        self.image_edited.emit()
        self.accept()

    def get_resized_image(self) -> Tuple[str, int, int]:
        """
        Returns:
            (image_path, width, height) of the final resized image.
        """
        r = self.item.boundingRect()
        w, h = int(r.width()), int(r.height())
        logger.debug("Resized image to %dx%d", w, h)
        return self.base_image_path, w, h
