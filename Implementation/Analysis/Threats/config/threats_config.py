"""
Module Name   : threats_config.py \n
Layer         : Configuration / Threats \n
Component ID  : N/A \n
Requirement ID: N/A \n
Version       : V 3.0 \n
Created By    : Vishnu Viswanath \n
Created On    : 2025-06-03 \n

Purpose:
--------
Defines the configuration schema for Threat property input fields used in dynamic
property panels. Enables consistent rendering of UI components through a centralized configuration.

Description:
------------
Specifies the fields displayed in the Threat property panel, including label, input type,
read-only status, signal handlers, and Save button properties.

Responsibilities:
-----------------
- Drive dynamic UI generation for Threats module
- Support signal-driven data updates
- Define readonly and multiselect configurations consistently

Structure:
----------
+-----------------------+----------------+--------------------------------------------+-------------------------------+
| Property Label        | Input Type     | Signal                                     | Additional Params             |
+=======================+================+============================================+===============================+
| ID                    | line           | None                                       | readonly=True                 |
| Name                  | multiline      | None                                       | readonly=True                 |
| Damage Scenarios      | multiselect    | on_threat_property_DS_changed              | -                             |
| TOE Configuration     | multiselect    | on_threat_property_toec_changed            | -                             |
| Misuse Cases          | multiselect    | on_threat_property_MS_changed              | -                             |
| Asset                 | line           | None                                       | readonly=True                 |
| Security Property     | line           | None                                       | readonly=True                 |
| Reasoning             | multiline      | on_threat_property_reasoning_changed       | -                             |
| Comments              | multiline      | on_threat_property_comment_changed         | -                             |
+-----------------------+----------------+--------------------------------------------+-------------------------------+

Dependencies:
-------------
- property_input_components.PropertyInputFactory (consumes this config)

Limitations:
------------
- External data loaders required for multiselect field population
- Does not support nested or conditional logic in inputs

Improvements:
-------------
- Add validation and contextual help support per field
- Enable dynamic signal-to-event mapping and value constraints

Change History:
---------------
+---------+------------+---------------------------------------------------+----------------------+
| Version | Date       | Change                                            | Author               |
+=========+============+===================================================+======================+
| V 3.0   | 2025-06-03 | Initial version for threat property config        | Vishnu Viswanath     |
+---------+------------+---------------------------------------------------+----------------------+
|         |            |                                                   |                      |
+---------+------------+---------------------------------------------------+----------------------+
|         |            |                                                   |                      |
+---------+------------+---------------------------------------------------+----------------------+
|         |            |                                                   |                      |
+---------+------------+---------------------------------------------------+----------------------+
"""


PROPERTY_CONFIG = [
    {"label": "ID", "type": "line", "readonly": True},
    {"label": "Name", "type": "multiline", "readonly": True},
    {"label": "Damage Scenarios", "type": "multiselect", "signal": "on_threat_property_DS_changed"},
    {"label": "TOE Configuration", "type": "multiselect", "signal": "on_threat_property_toec_changed"},
    {"label": "Misuse Cases", "type": "multiselect", "signal": "on_threat_property_MS_changed"},
    {"label": "Asset", "type": "line", "readonly": True},
    {"label": "Security Property", "type": "line", "readonly": True},
    {"label": "Reasoning", "type": "multiline", "signal": "on_threat_property_reasoning_changed"},
    {"label": "Comments", "type": "multiline", "signal": "on_threat_property_comment_changed"},
]

SAVE_BUTTON = {
    "enabled": True,
    "label": "Save"
}
