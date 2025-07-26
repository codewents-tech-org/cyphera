"""
Module Name   : security_controls_config.py  \n
Layer         : Configuration / Security Controls  \n
Component ID  : N/A  \n
Requirement ID: N/A  \n
Version       : V 3.0  \n
Created By    : Vishnu Viswanath  \n
Created On    : 2025-06-03  \n

Purpose:
--------
Defines the configuration schema for Security Control property input fields used in dynamic
property panels. Enables standardized UI rendering and event wiring for control components.

Description:
------------
Provides field-level configuration for Security Controls in the property panel UI.
Specifies input types, signal bindings, read-only status, and placeholders for dynamic items.

Responsibilities:
-----------------
- Describe all editable and displayable fields for a Security Control
- Emit change signals for relevant fields
- Allow item values (e.g., security goals) to be injected dynamically

Structure:
----------
+---------------------+----------------+-----------------------------------------------+--------------------------------------+
| Property Label      | Input Type     | Signal                                        | Additional Params                    |
+=====================+================+===============================================+======================================+
| ID                  | line           | None                                          | readonly=True                        |
| Name                | multiline      | on_scc_property_name_changed                  | -                                    |
| Security Goals      | multiselect    | on_scc_property_securityproperty_changed      | items=[] (to be set dynamically)     |
| Description         | multiline      | on_scc_property_description_changed           | -                                    |
| Comments            | multiline      | on_scc_property_comment_changed               | -                                    |
+---------------------+----------------+-----------------------------------------------+--------------------------------------+

Dependencies:
-------------
- property_input_components.PropertyInputFactory (consumes this config)
- Dynamic loader for Security Goals items (external binding)

Limitations:
------------
- Does not include field validation
- Security Goals item list must be injected at runtime

Improvements:
-------------
- Add item validation and contextual tooltips
- Introduce grouped or conditional field rendering

Change History:
---------------
+---------+------------+-------------------------------------------------------------+----------------------+
| Version | Date       | Change                                                      | Author               |
+=========+============+=============================================================+======================+
| V 3.0   | 2025-06-03 | Initial version for security control property config        | Vishnu Viswanath     |
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
        "signal": "on_scc_property_name_changed"
    },
    {
        "label": "Security Goals",
        "type": "multiselect",
        "signal": "on_scc_property_securityproperty_changed",
        "items": []  # To be set dynamically
    },
    {
        "label": "Description",
        "type": "multiline",
        "signal": "on_scc_property_description_changed"
    },
    {
        "label": "Comments",
        "type": "multiline",
        "signal": "on_scc_property_comment_changed"
    }
]

SAVE_BUTTON = {
    "enabled": True
}
