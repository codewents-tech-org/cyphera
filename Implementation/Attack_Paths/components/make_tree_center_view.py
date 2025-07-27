

from PyQt5.QtCore import QRectF

def center_tree_in_view(self):
    """
    Center the entire tree structure in the view without resetting zoom.
    """
    views = self.views()
    if not views:
        return  # No view attached

    view = views[0]
    scene_bounds: QRectF = self.itemsBoundingRect()  # tightly fits tree
    padding = 100

    # Expand bounding rect for padding
    padded_rect = scene_bounds.adjusted(-padding, 0, padding, padding)

    # Optional: Update scene rectangle so scrolling doesn't cut off
    self.setSceneRect(padded_rect)

    # Center view on the scene's center (not node by node)
    view.centerOn(padded_rect.center())
