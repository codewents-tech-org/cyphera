
"""
Module Name   : property_input_components.py \n
Layer         : Presentation / Shared Component \n
Component ID  : CY_CO_002 \n 
Requirement ID: N/A \n
Version       : V 3.0 \n
Created By    : Vishnu Viswanath \n
Created On  : 2025-05-16 \n

Purpose:
--------
Provides a reusable factory class (`PropertyInputFactory`) for dynamically generating 
styled property input widgets and Save buttons in PyQt5-based panels. This eliminates 
UI duplication and ensures consistency across modules like Assets, Threats, etc.

Description:
------------
Defines reusable UI components for dynamic property panels, supporting various input types
(QLineEdit, QTextEdit, MultiSelectComboBox, SingleSelectComboBox) with standardized styling and signal handling.

Responsibilities:
-----------------
- Eliminate UI duplication across modules (Assets, Threats, etc.)
- Dynamically generate labeled inputs
- Emit change signals or button click events with data payload

Signals
-------
+---------------------+----------------+-----------------------------+-----------------------------------------------+
| Trigger             | Signal Name    | Description                 | Payload Format                                |
+=====================+================+=============================+===============================================+
| Save clicked        | signal.emit    | Emitted on save action      | {"sender": str, "event": "save", "data": dict}|
+---------------------+----------------+-----------------------------+-----------------------------------------------+



Dependencies:
-------------
- PyQt5 (QtCore, QtWidgets)
- styles.property_panel_style
- components.MultiOptionSelector

Limitations:
------------
- Supported input types are fixed
- Validation not included
Improvements:
-------------
- Add input validation hooks for field-level verification
- Enable dynamic input type registration for more flexibility
- Refactor signal wiring for broader event compatibility

Change History:
---------------
+----------------+----------------------+---------------------------------------------+----------------------+
| Version        | Date                 | Change                                      | Author               |
+================+======================+=============================================+======================+
| V 3.0          | 2025-05-16           | Refactored to class-based architecture      | Vishnu Viswanath     |
+----------------+----------------------+---------------------------------------------+----------------------+
| V 3.0          | 2025-06-03           | Added 'singleselect' input type support     | Vishnu Viswanath     |
+----------------+----------------------+---------------------------------------------+----------------------+
|                |                      |                                             |                      |
+----------------+----------------------+---------------------------------------------+----------------------+
|                |                      |                                             |                      |
+----------------+----------------------+---------------------------------------------+----------------------+
"""
import logging

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (
        QLabel,
        QLineEdit,
        QTextEdit,
        QSpacerItem,
        QSizePolicy,
        QPushButton, 
        QComboBox
    )
    from components.table.multioption_selector import MultiSelectComboBox, ReadOnlyMultiSelectComboBox, NoWheelComboBox
    import styles.property_panel_style as property_panel_style
except ImportError as import_error:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.exception("Failed to import modules in generic_property_panel.py: %s", import_error)
    raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PropertyInputFactory:
    """
    A factory class to generate standardized property input widgets and save buttons 
    for dynamic property panels in a PyQt5 UI. It supports multiple input types 
    (single-line, multi-line, multi-select and singleselect dropdowns) 
    and handles styling and signal connections.
    """
    def __init__(self):
        self.STYLE_MAP = {
            "line": property_panel_style.property_singleline_input_style,
            "multiline": property_panel_style.property_multiline_input_style,
            "multiselect": property_panel_style.property_combobox_style,
            "multiselect1": property_panel_style.property_combobox_style,
            "singleselect": property_panel_style.property_combobox_style
        }

        self.HEIGHT_MAP = {
            "line": 50,
            "multiline": 130,
            "multiselect": 50,
            "multiselect1": 130,
            "singleselect": 50
        }
    def create_common_property_input(
        self, label_text: str, input_type: str,
        layout, controls_list, signal=None, items=None,setReadOnly=None
    ):
        """
        Create a styled property input widget and add it to the provided layout.

        Dynamically generates a labeled input field for use in the property panel.
        Supports single-line, multi-line, and multiselect inputs.

        Parameters:
        -----------
        self : QWidget
            The parent widget or container.
        label_text : str
            Label to display above the input.
        input_type : str
            Input control type: 'line', 'multiline', 'multiselect', 'multiselect1', 'singleselect'.
        layout : QVBoxLayout
            Layout to which the widgets are added.
        controls_list : list
            List storing [label, input_widget] pairs.
        signal : function, optional
            Signal to connect to the input change event.
        items : list[str], optional
            Dropdown values for multiselect inputs.

        Returns:
        --------
        QWidget
            Created input widget instance, or None on error.

        Raises:
        -------
        ValueError
            If input_type is unsupported.
        """
        try:
            label = QLabel(label_text)
            label.setStyleSheet(property_panel_style.property_label_style)
            layout.addWidget(label)

            if input_type == 'line':
                input_widget = QLineEdit()
            elif input_type == 'multiline':
                input_widget = QTextEdit()
            elif input_type == 'multiselect':
                input_widget = MultiSelectComboBox(items or [])
                input_widget.set_text('')
            elif input_type == 'multiselect1':
                input_widget = ReadOnlyMultiSelectComboBox(items or [])
                input_widget.set_text('')
            elif input_type == 'singleselect':
                input_widget = NoWheelComboBox()
                input_widget.addItems(items or [])
                input_widget.setCurrentIndex(0 if items else -1)


            else:
                raise ValueError("Unsupported input_type")

            input_widget.setFixedHeight(self.HEIGHT_MAP.get(input_type, 50))
            input_widget.setStyleSheet(self.STYLE_MAP.get(input_type, ""))
            layout.addWidget(input_widget)

            layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
            controls_list.append([label, input_widget]) 

            if signal:
                if isinstance(input_widget, QComboBox):
                    input_widget.currentTextChanged.connect(signal)
                elif hasattr(input_widget, "textChanged"):
                    input_widget.textChanged.connect(signal)
                elif hasattr(input_widget, "editTextChanged"):
                    input_widget.editTextChanged.connect(signal)
                else:
                    logger.warning(
                        "%s does not support text change signals.",
                        type(input_widget).__name__
                    )
            return input_widget
        except (ValueError, RuntimeError, Exception) as custom_error:
            logger.error(
                "Exception in create_common_property_input for '%s': %s",
                label_text,
                custom_error
            )
            return None


    def create_save_button(_self, layout, style: str, controls_list=None,
                        signal=None, sender="Property panel",
                        width: int = 270, height: int = 50) -> QPushButton:
        """
        Create a styled Save button and attach a signal emitter on click.

        Gathers values from provided widgets, constructs a structured payload,
        and emits it via the given signal.

        Parameters:
        -----------
        self : QWidget
            Parent widget or container.
        layout : QVBoxLayout
            Layout to which the button is added.
        style : str
            Stylesheet string applied to the button.
        controls_list : list, optional
            Pairs of QLabel and QWidget storing input fields.
        signal : pyqtSignal, optional
            Signal to emit the data payload.
        sender : str
            String to identify the emitting widget/component.
        width : int
            Button width. Default: 270.
        height : int
            Button height. Default: 50.

        Returns:
        --------
        QPushButton
            Configured Save button instance.

        Emits:
        -------
        signal : pyqtSignal
            JSON-serializable dict payload in the form::

                {
                    "sender": "Property panel",
                    "event": "save",
                    "data": {
                        "Field 1": "value",
                        "Field 2": "value"
                    }
                }

        Example:
        --------
        >>> save_button = create_save_button(self, layout, style, controls_list, signal)
        """
        try:
            save_button = QPushButton("Save")
            save_button.setFixedSize(width, height)
            save_button.setStyleSheet(style)
            layout.addWidget(save_button, alignment=Qt.AlignCenter)
            layout.addStretch()

            def on_click():
                if signal and controls_list:
                    data = {}
                    for label, widget in controls_list:
                        label_text = label.text()
                        if hasattr(widget, 'toPlainText'):
                            value = widget.toPlainText()
                        elif hasattr(widget, 'get_selected_items'):
                            value = widget.get_selected_items()
                        elif hasattr(widget, 'text'):
                            value = widget.text()
                        else:
                            value = ''
                        data[label_text] = value

                    payload = {
                        'sender': sender,
                        'event': 'save',
                        'data': data
                    }
                    signal.emit(payload)

            save_button.clicked.connect(on_click)
            return save_button

        except Exception as err:
            logger.error("Error in create_save_button: %s", err)
            return QPushButton("Error")
