"""
Module: Custom Graphics View      \n 
File: customgraphics_view.py      \n
Layer: UI / Graphics View Layer      \n
Component ID:          \n
Requirement IDs:       \n
Author: Vijaya karagi  \n
Created On: 2025-07-08     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Provides a custom QGraphicsView subclass that enables smooth zooming with mouse wheel
for scene navigation in tree visualization interfaces.

Description:
------------
The CustomGraphicsView extends QGraphicsView to enable zooming functionality using 
mouse wheel events. It scales the view based on a fixed zoom factor to improve 
usability when interacting with large tree structures in the QGraphicsScene.

Responsibilities
----------------
- Provide interactive zoom control using mouse wheel.
- Forward rendering responsibility to attached QGraphicsScene.
- Support zoom in/out with smooth scaling.

Dependencies:
-------------
- PyQt5.QtWidgets.QGraphicsView

Limitations
-----------
- Does not support zoom limits or centering on node.
- Pan/drag features must be enabled separately if needed.
- No zoom reset or keyboard controls yet.

Improvements
------------
- Add zoom limits and clamping.
- Add reset zoom and center view methods.
- Integrate drag-to-pan or middle-mouse panning.
- Improve smooth zoom via animation or QTimer.

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-07-08           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

from PyQt5.QtWidgets import QGraphicsView  
import logging

logger = logging.getLogger(__name__)

class CustomGraphicsView(QGraphicsView):
    """
    A custom QGraphicsView that supports interactive zooming via mouse wheel.

    This class enables users to zoom in and out on a QGraphicsScene using the
    scroll wheel, improving usability for large technical trees or diagrams.
    """
    def __init__(self, scene, parent=None):
        """
        Initializes the custom graphics view.

        Args:
            scene (QGraphicsScene): The graphics scene to display.
            parent (QWidget, optional): Optional parent widget.
        """
        super().__init__(scene, parent)
        self.zoom_factor = 1.15  # Set zoom factor

    def wheelEvent(self, event):
        """
        Handles mouse wheel event to scale the view.

        Args:
            event (QWheelEvent): Mouse wheel event that triggers zoom.
        """
        # Zoom in or out
        if event.angleDelta().y() > 0:  # Wheel up, zoom in
            self.scale(self.zoom_factor, self.zoom_factor)
        else:  # Wheel down, zoom out
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)

