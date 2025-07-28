

import sys
from PyQt5.QtWidgets import QGraphicsView  
import logging
logger = logging.getLogger(__name__)

class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.zoom_factor = 1.15  # Set zoom factor

    def wheelEvent(self, event):
        # Zoom in or out
        if event.angleDelta().y() > 0:  # Wheel up, zoom in
            self.scale(self.zoom_factor, self.zoom_factor)
        else:  # Wheel down, zoom out
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)



