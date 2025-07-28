"""
Module: MultiOption Selector    \n
File: multioption_selector.py   \n
Layer: UI / ComboBox Component Layer   \n
Component ID: CY_CO_012   \n
Requirement IDs:   \n
Author: Vishnu Viswanath   \n
Created On: 2025-05-14   \n
Version: V 3.0   \n

Purpose:
--------
Provides enhanced versions of PyQt5 `QComboBox` widgets with multi-selection capabilities using checkboxes,
including editable and read-only modes. These components allow dynamic selection and user feedback 
while maintaining a clean and customizable UI.

Description:
------------
This module defines multiple specialized combo box components extending PyQt5's `QComboBox`. Key features include:
- Checkbox-based multi-select
- Read-only display variants
- Custom popup behavior for item display
- Consistent styling and layout integration

Responsibilities
----------------
- Render a combo box with selectable checkboxes as options
- Emit selection data and allow inline updates of displayed text
- Provide flexible subclassing options for specific interaction behaviors
- Prevent unwanted interaction like mouse wheel scrolling

Signals
-------
+---------------------+----------------------+-----------------------------+----------------------+
| Trigger             | Signal Origin        | Description                 | Payload Format       |
+=====================+======================+=============================+======================+
| Item toggled        | toggle_item          | Handles item check/uncheck  | Updated items list   |
+---------------------+----------------------+-----------------------------+----------------------+
| Combo clicked       | eventFilter          | Shows popup menu            | Click event          |
+---------------------+----------------------+-----------------------------+----------------------+

Dependencies:
-------------
- PyQt5 (QtWidgets, QtCore)
- styles.combo_box_style
- logging

Limitations
-----------
- No native keyboard selection or filtering
- Manual management of selected items
- Delegate customization (e.g., dropdown or text input) not yet modularized

Improvements
------------
- Add keyboard navigation and search filter
- Support nested item structures or grouped categories
- Add input validation and constraints for selected values

Change History:
---------------
+----------------+----------------------+-----------------------------+----------------------+
| Version        | Date                 | Change                      | Author               |
+================+======================+=============================+======================+
| V 3.0          | 2025-05-14           | Initial version created     | Vishnu Viswanath     |
+----------------+----------------------+-----------------------------+----------------------+
|                |                      |                             |                      |
+----------------+----------------------+-----------------------------+----------------------+
|                |                      |                             |                      |
+----------------+----------------------+-----------------------------+----------------------+
|                |                      |                             |                      |
+----------------+----------------------+-----------------------------+----------------------+
"""


import logging
logger = logging.getLogger(__name__)
try:
    from PyQt5.QtWidgets import (
    # pylint: disable=no-name-in-module, import-error
        QComboBox, QDialog, QVBoxLayout, QScrollArea, QWidget,
        QCheckBox, QHBoxLayout
    )
    from PyQt5.QtCore import Qt, QEvent
    # pylint: disable=no-name-in-module, import-error
    # pylint: disable=no-name-in-module, import-error

    from styles.combo_box_style import COMBOBOX_STYLE
except ImportError as e:
    logger.warning(f"Mocking PyQt5 elements due to import error: {e}")


POPUP_MAX_HEIGHT = 210

logger = logging.getLogger(__name__)
class SharedComboBehavior:
    """
    Mixin class providing shared behaviors for custom combo boxes.
    Includes handling of display text, mouse wheel disable, and popup triggers.
    """
    # pylint: disable=invalid-name
    def eventFilter(self, obj, event):
        """
        Intercept mouse release events on line edit to trigger popup display.

        Args:
            obj (QObject): The object where the event occurred.
            event (QEvent): The event being processed.

        Returns:
            bool: True if the event was handled, else False.
        """
        try:
            if obj == self.lineEdit() and event.type() == QEvent.MouseButtonRelease:
                self.show_popup()
                return True
            return QComboBox.eventFilter(self, obj, event)
        except (ValueError, AttributeError) as e:
            logger.exception("Error in eventFilter: %s", e)
            return False

    def get_display_text(self):
        """
        Get display-safe version of selected items.

        Args:
            None

        Returns:
            list: List of string values before any '::' suffix.
        """
        try:
            return [item.split("::")[0] for item in self.selected_items_list]
        except (ValueError, AttributeError) as e:
            logger.exception("Error in get_display_text: %s", e)
            return None

    def update_text(self):
        """
        Update the combo box's visible text from selected items.

        Args:
            None

        Returns:
            None
        """
        try:
            self.setCurrentText(
                ", ".join(self.get_display_text())
                )
            self.lineEdit().setCursorPosition(0)
        except (ValueError, AttributeError) as e:
            logger.exception("Error in update_text: %s", e)

    def selected_items(self):
        """
        Return the list of selected items.

        Args:
            None

        Returns:
            list: Selected item strings.
        """
        try:
            return self.selected_items_list
        except (ValueError, AttributeError) as e:
            logger.exception("Error in selected_items: %s", e)
            return []

    # pylint: disable=invalid-name
    def wheelEvent(self, event):
        """
        Disable mouse wheel scrolling behavior.

        Args:
            event (QWheelEvent): Mouse wheel event.

        Returns:
            None
        """
        try:
            event.ignore()
        except (ValueError, AttributeError) as e:
            logger.exception("Error in wheelEvent: %s", e)

class MultiSelectComboBox(QComboBox, SharedComboBehavior):
    """Custom combo box allowing multi-select using checkboxes."""
    def __init__(self, items, *args, **kwargs):
        """
        Initialize MultiSelectComboBox with checkbox-based multi-selection.

        Args:
            items (list): List of items to show.
            *args: Positional arguments for QComboBox.
            **kwargs: Keyword arguments for QComboBox.

        Returns:
            None
        """
        try:
            super().__init__(*args, **kwargs)
            self.setEditable(True)
            self.setInsertPolicy(QComboBox.NoInsert)
            self.lineEdit().setReadOnly(True)
            self.setDuplicatesEnabled(False)

            self.additem(items)
            self.selected_items_list = []
            self.checkboxes = {}  # Store checkboxes for reference


            self.checkboxes = {}  # Store checkboxes for reference

            # Event filter to handle mouse clicks on the line edit.
            self.lineEdit().installEventFilter(self)

            self.update_items()
            self.activated.connect(self.show_popup)
            self.lineEdit().installEventFilter(self)
        except (ValueError, AttributeError) as e:
            logger.exception("Error initializing MultiSelectComboBox: %s", e)


    def additem(self, items):
        """
        Add items to the combo box.

        Args:
            items (list): List of string items.

        Returns:
            None
        """
        try:
            self.addItems(items)
            self.items = items
        except (ValueError, AttributeError) as e:
            logger.exception("Error in additem: %s", e)

    def update_items(self):
        """
        Update the combo box items and refresh display.

        Args:
            None

        Returns:
            None
        """
        try:
            self.clear()
            for item in self.items:
                self.addItem(item)
            self.setCurrentText(
                ", ".join(self.selected_items_list)
                )
        except (ValueError, AttributeError) as e:
            logger.exception("Error in update_items: %s", e)

    def select_row(self, item):
        """
        Handle click on a row to toggle selection.

        Args:
            item (str): Item to toggle selection for.

        Returns:
            None
        """
        try:
            if item in self.selected_items_list:
                self.selected_items_list.remove(item)
                checked = False
            else:
                self.selected_items_list.append(item)
                checked = True

            self.update_text()

            # Update checkbox state visually
            if item in self.checkboxes:
                self.checkboxes[item].setChecked(checked)
        except (ValueError, AttributeError) as e:
            logger.exception("Error in select_row: %s", e)


    def show_popup(self):
        """
        Show the popup with checkbox items.

        Args:
            None

        Returns:
            None
        """
        try:
            if not self.items:  # Do not open popup if no items exist
                return

            popup = QDialog(self, Qt.Popup)
            popup.setWindowFlags(Qt.Popup)
            popup.setWindowTitle("")
            layout = QVBoxLayout(popup)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            scroll = QScrollArea(popup)
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(2, 2, 2, 2)
            content_layout.setSpacing(2)

            self.checkboxes.clear()  # Reset stored checkboxes

            for item in self.items:
                row_widget = QWidget(content_widget)
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(2)

                cb = QCheckBox(item, row_widget)
                cb.setChecked(item in self.selected_items_list)
                cb.setStyleSheet(COMBOBOX_STYLE)

                cb.stateChanged.connect(lambda state, i=item: self.toggle_item(i,
    state == Qt.Checked))
                self.checkboxes[item] = cb  # Store checkbox reference

                # Make the whole row clickable to toggle selection
                row_widget.mousePressEvent = lambda event, i=item: self.select_row(i)

                row_layout.addWidget(cb)
                row_widget.setLayout(row_layout)
                content_layout.addWidget(row_widget)

            content_widget.setLayout(content_layout)
            scroll.setWidget(content_widget)
            layout.addWidget(scroll)
            popup.setLayout(layout)

            popup.setFixedWidth(self.width())

            # Adjust popup height dynamically based on number of items
            item_height = 30  # Approximate height of one item
            max_popup_height = min(210, len(self.items) * item_height + 10)  # Limit max height
            popup.setFixedHeight(max_popup_height)

            popup.move(self.mapToGlobal(self.rect().bottomLeft()))
            popup.exec_()
        except (ValueError, AttributeError) as e:
            logger.exception("Error in show_popup: %s", e)


    def toggle_item(self, item, checked):
        """
        Toggle the checked state of an item.

        Args:
            item (str): The item to toggle.
            checked (bool): Whether the item is checked or not.

        Returns:
            None
        """
        try:
            if checked:
                if item not in self.selected_items_list:
                    self.selected_items_list.append(item)
            else:
                if item in self.selected_items_list:
                    self.selected_items_list.remove(item)
            self.update_text()
        except (ValueError, AttributeError) as e:
            logger.exception("Error in toggle_item: %s", e)


    def set_text(self, text):
        """
        Set combo box text and update selected items.

        Args:
            text (str or list): Items to be shown as selected.

        Returns:
            None
        """
        try:
            if isinstance(text, list):
                text = ", ".join(text)
            items = [item.strip() for item in text.split(", ") if item.strip() in self.items]
            self.selected_items_list = items
            self.setCurrentText(
                ",".join(items)
                                )
            self.update_text()
        except (ValueError, AttributeError) as e:
            logger.exception("Error in set_text: %s", e)

class TSMultiSelectComboBox(QComboBox, SharedComboBehavior):
    """Custom combo box allowing multi-select using checkboxes."""
    def __init__(self, items, *args, **kwargs):
        """
        Initialize TSMultiSelectComboBox with given items.

        Args:
            items (list): List of item labels.
            *args: Additional arguments passed to QComboBox.
            **kwargs: Additional keyword arguments passed to QComboBox.

        Returns:
            None
        """
        try:
            super().__init__(*args, **kwargs)
            self.setEditable(True)
            self.setInsertPolicy(QComboBox.NoInsert)
            self.lineEdit().setReadOnly(True)
            self.setDuplicatesEnabled(False)

            self.additem(items)
            self.selected_items_list = []
            self.checkboxes = {}  # Store checkboxes for reference

            # Event filter to handle mouse clicks on the line edit.
            self.checkboxes = {}  # Store checkboxes for reference

            # Event filter to handle mouse clicks on the line edit.
            self.lineEdit().installEventFilter(self)
        except (ValueError, AttributeError) as e:
            logger.exception("Error initializing MultiSelectComboBox: %s", e)

    def additem(self, items):
        """
        Add items to the combo box.

        Args:
            items (list): List of string items.

        Returns:
            None
        """
        try:
            self.addItems(items)
            self.items = items
        except (ValueError, AttributeError) as e:
            logger.exception("Error in additem: %s", e)

    def update_items(self):
        """
        Update the combo box display text based on selected items.

        Args:
            None

        Returns:
            None
        """
        try:
            self.clear()
            self.setCurrentText(
                ", ".join(self.get_display_text())
                )
        except (ValueError, AttributeError) as e:
            logger.exception("Error in update_items: %s", e)

    def show_popup(self):
        """
        Display a popup dialog containing all available items as checkboxes.

        Args:
            None

        Returns:
            None
        """
        try:
            if not self.items:  # Do not open popup if no items exist
                return

            popup = QDialog(self, Qt.Popup)
            popup.setWindowFlags(Qt.Popup)
            popup.setWindowTitle("")
            layout = QVBoxLayout(popup)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            scroll = QScrollArea(popup)
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(2, 2, 2, 2)
            content_layout.setSpacing(2)

            self.checkboxes.clear()  # Reset stored checkboxes

            for item in self.items:
                row_widget = QWidget(content_widget)
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(2)

                cb = QCheckBox(item, row_widget)
                cb.setChecked(item in self.selected_items_list)
                cb.setStyleSheet(COMBOBOX_STYLE)

                cb.stateChanged.connect(lambda state, i=item: self.toggle_item(i,
    state == Qt.Checked))
                self.checkboxes[item] = cb  # Store checkbox reference

                # Make the whole row clickable to toggle selection
                row_widget.mousePressEvent = lambda event, i=item: self.select_row(i)

                row_layout.addWidget(cb)
                row_widget.setLayout(row_layout)
                content_layout.addWidget(row_widget)

            content_widget.setLayout(content_layout)
            scroll.setWidget(content_widget)
            layout.addWidget(scroll)
            popup.setLayout(layout)

            popup.setFixedWidth(self.width())

            # Adjust popup height dynamically based on number of items
            item_height = 30  # Approximate height of one item
            max_popup_height = min(210, len(self.items) * item_height + 10)  # Limit max height
            popup.setFixedHeight(max_popup_height)

            popup.move(self.mapToGlobal(self.rect().bottomLeft()))
            popup.exec_()
        except (ValueError, AttributeError) as e:
            logger.exception("Error in show_popup: %s", e)

    def toggle_item(self, item, checked):
        """
        Toggle the selection state of an item.

        Args:
            item (str): The item to modify.
            checked (bool): The new checked state.

        Returns:
            None
        """
        try:
            if checked:
                if item not in self.selected_items_list:
                    self.selected_items_list.append(item)
            else:
                if item in self.selected_items_list:
                    self.selected_items_list.remove(item)
            self.update_text()
        except (ValueError, AttributeError) as e:
            logger.exception("Error in toggle_item: %s", e)


    def select_row(self, item):
        """
        Toggle selection status of a row item when clicked.

        Args:
            item (str): The item name.

        Returns:
            None
        """
        try:
            if item in self.selected_items_list:
                self.selected_items_list.remove(item)
                checked = False
            else:
                self.selected_items_list.append(item)
                checked = True

            self.update_text()

            # Update checkbox state visually
            if item in self.checkboxes:
                self.checkboxes[item].setChecked(checked)
        except (ValueError, AttributeError) as e:
            logger.exception("Error in select row: %s", e)

    def set_text(self, text):
        """
        Update selection using given text string or list.

        Args:
            text (str or list): Selected item labels.

        Returns:
            None
        """
        try:
            if isinstance(text, list):
                text = ", ".join(text)

            items = [item.strip() for item in text.split(",") if item.strip() in self.items]
            self.selected_items_list = items

            self.setCurrentText(
                ", ".join(self.get_display_text())
                )
            self.update_text()
        except (ValueError, AttributeError) as e:
            logger.exception("Error in set_text: %s", e)


class ReadOnlyMultiSelectComboBox(QComboBox, SharedComboBehavior):
    """Custom combo box allowing multi-select using checkboxes."""
    def __init__(self, items, *args, **kwargs):
        """
        Initialize a read-only combo box with checkboxes shown but disabled.

        Args:
            items (list): List of combo box options.
            *args: Positional arguments for QComboBox.
            **kwargs: Keyword arguments for QComboBox.

        Returns:
            None
        """
        try:
            super().__init__(*args, **kwargs)
            self.setEditable(True)
            self.setInsertPolicy(QComboBox.NoInsert)
            self.lineEdit().setReadOnly(True)  # Make line edit read-only
            self.setDuplicatesEnabled(False)

            # Initialize items and selected list
            self.items = items
            self.selected_items_list = []
            self.checkboxes = {}  # Store checkboxes for reference

            # Install event filter to handle click on the line edit.
            self.lineEdit().installEventFilter(self)
            # Add items to the combobox and update the display text
            self.additem(items)
            self.update_text()
        except (ValueError, AttributeError) as e:
            logger.exception("Error initializing MultiSelectComboBox: %s", e)

    def additem(self, items):
        """
        Add items to the combo box.

        Args:
            items (list): Items to add.

        Returns:
            None
        """
        try:
            self.addItems(items)
        except (ValueError, AttributeError) as e:
            logger.exception("Error in additem: %s", e)

    def update_items(self):
        """
        Refresh displayed items and update visual state.

        Args:
            None

        Returns:
            None
        """
        try:
            self.clear()
            self.addItems(self.items)
            self.setCurrentText(
                ", ".join(self.get_display_text())
                )
        except (ValueError, AttributeError) as e:
            logger.exception("Error in update_items: %s", e)

    def show_popup(self):
        """
        Show non-interactive popup with pre-selected items.

        Args:
            None

        Returns:
            None
        """
        try:
            if not self.items:  # Do not open popup if no items exist
                return

            popup = QDialog(self, Qt.Popup)
            popup.setWindowFlags(Qt.Popup)
            popup.setWindowTitle("")
            layout = QVBoxLayout(popup)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            scroll = QScrollArea(popup)
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(2, 2, 2, 2)
            content_layout.setSpacing(2)

            self.checkboxes.clear()  # Reset stored checkboxes

            for item in self.items:
                row_widget = QWidget(content_widget)
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(2)

                cb = QCheckBox(item, row_widget)
                cb.setChecked(item in self.selected_items_list)
                cb.setEnabled(False)  # Disable the checkbox so user cannot change selection
                cb.setStyleSheet(COMBOBOX_STYLE)


                self.checkboxes[item] = cb  # Store checkbox reference

                row_layout.addWidget(cb)
                row_widget.setLayout(row_layout)
                content_layout.addWidget(row_widget)

            content_widget.setLayout(content_layout)
            scroll.setWidget(content_widget)
            layout.addWidget(scroll)
            popup.setLayout(layout)

            popup.setFixedWidth(self.width())

            # Adjust popup height dynamically based on number of items
            item_height = 30  # Approximate height of one item
            max_popup_height = min(210, len(self.items) * item_height + 10)
            popup.setFixedHeight(max_popup_height)

            popup.move(self.mapToGlobal(self.rect().bottomLeft()))
            popup.exec_()
        except (ValueError, AttributeError) as e:
            logger.exception("Error in show_popup: %s", e)


    def toggle_item(self, item, checked):
        """
        Toggle selection status of a row item when clicked.

        Args:
            item (str): The item name.

        Returns:
            None
        """
        try:
            if checked:
                if item not in self.selected_items_list:
                    self.selected_items_list.append(item)
            else:
                if item in self.selected_items_list:
                    self.selected_items_list.remove(item)
            self.update_text()
        except (ValueError, AttributeError) as e:
            logger.exception("Error in toggle_item: %s", e)

    def set_text(self, text):
        """
        Set pre-selected text for display (read-only).

        Args:
            text (str or list): Items to show as selected.

        Returns:
            None
        """
        try:
            if isinstance(text, list):
                text = ", ".join(text)

            items = [item.strip() for item in text.split(",") if item.strip() in self.items]
            self.selected_items_list = items

            self.setCurrentText(
                ", ".join(self.get_display_text())
                )
            self.update_text()
        except (ValueError, AttributeError) as e:
            logger.exception("Error in set_text: %s", e)


class CustomComboBox(QComboBox, SharedComboBehavior):
    """Custom combo box allowing multi-select using checkboxes."""
    def __init__(self, items, *args, **kwargs):
        """
        Initialize the combo box with given items.

        Args:
            items (list): Initial list of options.
            *args: Positional arguments to QComboBox.
            **kwargs: Keyword arguments to QComboBox.

        Returns:
            None
        """
        try:
            super().__init__(*args, **kwargs)
            self.setEditable(True)
            self.setInsertPolicy(QComboBox.NoInsert)
            self.lineEdit().setReadOnly(True)
            self.setDuplicatesEnabled(False)
            self.add_items(items)
            self.lineEdit().installEventFilter(self)
            self.setFocusPolicy(Qt.StrongFocus)
        except (ValueError, AttributeError) as e:
            logger.exception("Error initializing MultiSelectComboBox: %s", e)

    def add_items(self, items):
        """
        Add a list of items to the combo box.

        Args:
            items (list): List of string items to add.

        Returns:
            None
        """
        try:
            self.addItems(items)
            self.items = items
        except (ValueError, AttributeError) as e:
            logger.exception("Error in additem: %s", e)

    # pylint: disable=invalid-name
    def eventFilter(self, obj, event):
        """
        Override eventFilter to show popup when clicked.

        Args:
            obj (QObject): The event target object.
            event (QEvent): The event being filtered.

        Returns:
            bool: True if handled, otherwise passes to super.
        """
        try:
            if obj == self.lineEdit() and event.type() == QEvent.MouseButtonRelease:
                self.showPopup()
                return True

            return super().eventFilter(obj, event)
        except (ValueError, AttributeError) as e:
            logger.exception("Error in eventFilter: %s", e)

    # pylint: disable=invalid-name
    def showPopup(self):
        """
        Display the combo box dropdown and resize based on content.

        Args:
            None

        Returns:
            None
        """
        try:
            super().showPopup()
            popup = self.view()
            # Calculate the maximum width required for the items
            max_width = max(
                popup.fontMetrics().width(popup.model().data(popup.model().index(i, 0)))
                 for i in range(popup.model().rowCount())
                 )
            # Set the width of the popup to fit the widest item
            popup.setFixedWidth(max_width + 20)  # Adding some padding
        except (ValueError, AttributeError) as e:
            logger.exception("Error in show_popup: %s", e)


    def set_text(self, text):
        """
        Set the combo box text to the first word of input.

        Args:
            text (str): The full text input.

        Returns:
            None
        """
        try:
            self.setCurrentText(
                text.split(" ")[0]
                )
        except (ValueError, AttributeError) as e:
            logger.exception("Error in set_text: %s", e)



class CustomComboBoxLeave(CustomComboBox):
    """Custom combo box allowing multi-select using checkboxes."""
    def __init__(self, items, *args, **kwargs):
        """
        Initialize the combo box and connect change handler.

        Args:
            items (list): List of combo box options.
            *args: Additional arguments for QComboBox.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        try:
            super().__init__(items, *args, **kwargs)
            self.currentTextChanged.connect(self.set_text)
        except (ValueError, AttributeError) as e:
            logger.exception("Error initializing MultiSelectComboBox: %s", e)

    def set_text(self, text):
        """
        Update displayed text with the first word from the given input.

        Args:
            text (str): Input text value.

        Returns:
            None
        """
        try:
            self.setCurrentText(
                text.strip().split(" ")[0]
                )
        except (ValueError, AttributeError) as e:
            logger.exception("Error in set_text: %s", e)

# pylint: disable=too-few-public-methods
class NoWheelComboBox(QComboBox):
    """ComboBox subclass that disables wheel scroll."""
    # pylint: disable=invalid-name
    def wheelEvent(self, event):
        """
        Override the wheel event to ignore scrolling.

        Args:
            event (QWheelEvent): Mouse wheel scroll event.

        Returns:
            None
        """
        event.ignore()
