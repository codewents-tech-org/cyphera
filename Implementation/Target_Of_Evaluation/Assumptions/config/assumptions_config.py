"""
Module Name   : assumptions_config.py  \n
Layer         : Configuration / Assumptions  \n
Component ID  : N/A  \n
Requirement ID: N/A  \n
Version       : V 3.0  \n
Created By    : Vishnu Viswanath  \n
Created On    : 2025-06-03  \n

Purpose:
--------
Defines the configuration schema for Assumption property input fields used in dynamic
property panels. Provides a lightweight configuration for editable fields and save functionality.

Description:
------------
Specifies the field definitions used in the Assumptions property panel, including
editable text fields and associated signal handlers. Also defines Save button configuration.

Responsibilities:
-----------------
- Define editable and readonly fields for Assumptions UI
- Wire up signals for change tracking
- Configure save button state

Structure:
----------
+---------------------+----------------+-----------------------------------------------+-------------------------------+
| Property Label      | Input Type     | Signal                                        | Additional Params             |
+=====================+================+===============================================+===============================+
| ID                  | line           | None                                          | readonly=True                 |
| Name                | multiline      | on_assum_property_name_changed                | -                             |
| Comments            | multiline      | on_assum_property_comment_changed             | -                             |
+---------------------+----------------+-----------------------------------------------+-------------------------------+

Dependencies:
-------------
- property_input_components.PropertyInputFactory (consumes this config)

Limitations:
------------
- No validation or conditional logic applied
- Minimal configuration (assumptions are simple entities)

Improvements:
-------------
- Add support for default values and validations
- Expand to include metadata or grouping options

Change History:
---------------
+---------+------------+-------------------------------------------------------------+----------------------+
| Version | Date       | Change                                                      | Author               |
+=========+============+=============================================================+======================+
| V 3.0   | 2025-06-03 | Initial version for assumptions property config             | Vishnu Viswanath     |
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
        "label": "Assumptions",
        "type": "multiline",
        "signal": "on_assum_property_name_changed"
    },
    {
        "label": "Comments",
        "type": "multiline",
        "signal": "on_assum_property_comment_changed"
    }
]

SAVE_BUTTON = {
    "enabled": True
}
