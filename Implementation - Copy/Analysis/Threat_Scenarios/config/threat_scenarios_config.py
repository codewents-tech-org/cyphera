"""
Module Name   : threat_scenarios_config.py \n
Layer         : Configuration / Threat Scenarios \n
Component ID  : N/A \n
Requirement ID: N/A \n
Version       : V 3.0 \n
Created By    : Vishnu Viswanath \n
Created On    : 2025-06-03 \n

Purpose:
--------
Defines the configuration schema for Threat Scenario property input fields used in dynamic
property panels. Enables the UI to render inputs consistently based on declarative configuration.

Description:
------------
Specifies the input fields shown for a Threat Scenario in the property panel,
including input type, label, read-only status, and optional signal handlers.
Also configures the Save button behavior.

Responsibilities:
-----------------
- Provide structured input metadata for Threat Scenario UI panels
- Support readonly and editable field definitions
- Configure signal mappings for data change tracking

Structure:
----------
+---------------------+----------------+------------------------------------------+-------------------------------+
| Property Label      | Input Type     | Signal                                   | Additional Params             |
+=====================+================+==========================================+===============================+
| ID                  | line           | None                                     | readonly=True                 |
| Threat              | multiline      | None                                     | readonly=True                 |
| Damage Scenarios    | multiline      | None                                     | readonly=True                 |
| TOE Configuration   | multiselect1   | None                                     | -                             |
| Reasoning           | multiline      | on_TS_property_reasoning_changed         | -                             |
| Comments            | multiline      | on_TS_property_comment_changed           | -                             |
+---------------------+----------------+------------------------------------------+-------------------------------+

Dependencies:
-------------
- property_input_components.PropertyInputFactory (consumes this config)

Limitations:
------------
- Input validation and item population for multiselect1 must be handled externally
- Read-only fields do not support interactivity or dynamic changes

Improvements:
-------------
- Support dynamic loading of TOE Configuration options
- Add validation hooks and conditional visibility options

Change History:
---------------
+---------+------------+-----------------------------------------------------+----------------------+
| Version | Date       | Change                                              | Author               |
+=========+============+=====================================================+======================+
| V 3.0   | 2025-06-03 | Initial version for threat scenario property config | Vishnu Viswanath     |
+---------+------------+-----------------------------------------------------+----------------------+
|         |            |                                                     |                      |
+---------+------------+-----------------------------------------------------+----------------------+
|         |            |                                                     |                      |
+---------+------------+-----------------------------------------------------+----------------------+
|         |            |                                                     |                      |
+---------+------------+-----------------------------------------------------+----------------------+
"""


PROPERTY_CONFIG = [
    {"label": "ID", "type": "line", "readonly": True},

    {"label": "Threat", "type": "multiline", "readonly": True},

    {"label": "Damage Scenarios", "type": "multiline", "readonly": True},

    {"label": "TOE Configuration", "type": "multiselect1"},

    {"label": "Reasoning", "type": "multiline", "signal": "on_TS_property_reasoning_changed"},

    {"label": "Comments", "type": "multiline", "signal": "on_TS_property_comment_changed"},
]

SAVE_BUTTON = {
    "enabled": True
}
