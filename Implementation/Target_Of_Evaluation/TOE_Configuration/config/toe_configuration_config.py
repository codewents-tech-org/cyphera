"""
Module Name   : toe_configuration_config.py  \n
Layer         : Configuration / TOE Configuration  \n
Component ID  : N/A  \n
Requirement ID: N/A  \n
Version       : V 3.0  \n
Created By    : Vishnu Viswanath  \n
Created On    : 2025-06-03  \n

Purpose:
--------
Defines the configuration schema for TOE (Target of Evaluation) Configuration
property input fields used in dynamic property panels. Supports structured UI generation
with change tracking via signals.

Description:
------------
Lists the editable and readonly fields used for TOE Configuration entities in
property panels, with signal connections for interactive updates and a Save button definition.

Responsibilities:
-----------------
- Define field metadata for TOE Configuration UI components
- Trigger signals on input change for external handling
- Enable consistent Save button behavior

Structure:
----------
+---------------------+----------------+-----------------------------------------------+-------------------------------+
| Property Label      | Input Type     | Signal                                        | Additional Params             |
+=====================+================+===============================================+===============================+
| ID                  | line           | None                                          | readonly=True                 |
| Name                | multiline      | on_toec_property_name_changed                 | -                             |
| Description         | multiline      | on_toec_property_description_changed          | -                             |
| Comments            | multiline      | on_toec_property_comment_changed              | -                             |
+---------------------+----------------+-----------------------------------------------+-------------------------------+

Dependencies:
-------------
- property_input_components.PropertyInputFactory (consumes this config)

Limitations:
------------
- No support for dynamic field visibility or validation
- Field values must be handled externally

Improvements:
-------------
- Add support for field validation and formatting
- Integrate conditional rendering based on entity context

Change History:
---------------
+---------+------------+-------------------------------------------------------------+----------------------+
| Version | Date       | Change                                                      | Author               |
+=========+============+=============================================================+======================+
| V 3.0   | 2025-06-03 | Initial version for TOE configuration property config       | Vishnu Viswanath     |
+---------+------------+-------------------------------------------------------------+----------------------+
|         |            |                                                             |                      |
+---------+------------+-------------------------------------------------------------+----------------------+
|         |            |                                                             |                      |
+---------+------------+-------------------------------------------------------------+----------------------+
|         |            |                                                             |                      |
+---------+------------+-------------------------------------------------------------+----------------------+
"""


PROPERTY_CONFIG = [
    {
        "label": "ID",
        "type": "line",
        "readonly": True
    },
    {
        "label": "Name",
        "type": "multiline",
        "signal": "on_toec_property_name_changed"
    },
    {
        "label": "Description",
        "type": "multiline",
        "signal": "on_toec_property_description_changed"
    },
    {
        "label": "Comments",
        "type": "multiline",
        "signal": "on_toec_property_comment_changed"
    }
]

SAVE_BUTTON = {
    "enabled": True
}
