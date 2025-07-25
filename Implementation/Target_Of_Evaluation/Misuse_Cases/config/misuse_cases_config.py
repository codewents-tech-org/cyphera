"""
Module Name   : misuse_cases_config.py  \n
Layer         : Configuration / Misuse Cases  \n
Component ID  : N/A  \n
Requirement ID: N/A  \n
Version       : V 3.0  \n
Created By    : Vishnu Viswanath  \n
Created On    : 2025-06-03  \n

Purpose:
--------
Defines the configuration schema for Misuse Case property input fields used in dynamic
property panels. Supports UI field generation and signal-based data binding.

Description:
------------
Outlines the field configurations for Misuse Cases shown in the UI property panel.
Provides editable and readonly field definitions along with signal events and save button logic.

Responsibilities:
-----------------
- Enable dynamic rendering of Misuse Case input fields
- Support signal emissions for tracking changes
- Define minimal structure for UI reuse

Structure:
----------
+---------------------+----------------+-----------------------------------------------+-------------------------------+
| Property Label      | Input Type     | Signal                                        | Additional Params             |
+=====================+================+===============================================+===============================+
| ID                  | line           | None                                          | readonly=True                 |
| Name                | multiline      | on_misusecase_property_name_changed           | -                             |
| Comments            | multiline      | on_misusecase_property_comment_changed        | -                             |
+---------------------+----------------+-----------------------------------------------+-------------------------------+

Dependencies:
-------------
- property_input_components.PropertyInputFactory (consumes this config)

Limitations:
------------
- No field validation or conditional logic
- Basic configuration — no external references or dependencies

Improvements:
-------------
- Add validation rules for required fields
- Enable grouping or tagging options for complex use cases

Change History:
---------------
+---------+------------+-------------------------------------------------------------+----------------------+
| Version | Date       | Change                                                      | Author               |
+=========+============+=============================================================+======================+
| V 3.0   | 2025-06-03 | Initial version for misuse cases property config            | Vishnu Viswanath     |
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
        "signal": "on_misusecase_property_name_changed"
    },
    {
        "label": "Comments",
        "type": "multiline",
        "signal": "on_misusecase_property_comment_changed"
    }
]

SAVE_BUTTON = {
    "enabled": True
}
