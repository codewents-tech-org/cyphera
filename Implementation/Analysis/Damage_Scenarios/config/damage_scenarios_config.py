"""
Module Name   : damage_scenarios_config.py \n
Layer         : Configuration / Damage Scenarios \n
Component ID  : N/A \n
Requirement ID: N/A \n
Version       : V 3.0 \n
Created By    : Vishnu Viswanath \n
Created On    : 2025-06-03 \n

Purpose:
--------
Defines the configuration schema for Damage Scenario property input fields used in dynamic
property panels. This allows the UI layer to render consistent input widgets
based on configuration rather than hardcoded logic.

Description:
------------
Specifies the input fields shown for a Damage Scenario in the property panel,
including type, labels, readonly status, selectable items, and signal handlers.
Also defines the configuration for the Save button appearance and behavior.

Responsibilities:
-----------------
- Provide a declarative config for UI input generation
- Define signal mappings for property changes
- Standardize save button styling across the Damage Scenario module

Structure:
----------
+---------------------+----------------+------------------------------------------+--------------------------------------+
| Property Label      | Input Type     | Signal                                   | Additional Params                    |
+=====================+================+==========================================+======================================+
| ID                  | line           | None                                     | readonly=True                        |
| Name                | multiline      | on_DS_property_name_changed              | -                                    |
| Impact              | singleselect   | on_DS_property_impact_changed            | items=DS_impact_menu                 |
| Impact Category     | multiselect    | on_DS_property_impactcategory_changed    | items=DS_impactcatagory_menu         |
| Reasoning           | multiline      | on_DS_property_description_changed       | -                                    |
| Comments            | multiline      | on_DS_property_comment_changed           | -                                    |
+---------------------+----------------+------------------------------------------+--------------------------------------+

Dependencies:
-------------
- models.helper.DS_impact_menu
- models.helper.DS_impactcatagory_menu
- property_input_components.PropertyInputFactory (consumes this config)

Limitations:
------------
- Field validation logic must be handled externally
- Input types are limited to supported widget classes

Improvements:
-------------
- Add field-level validation or conditional visibility
- Support dynamic field types and grouping

Change History:
---------------
+---------+------------+---------------------------------------------------+----------------------+
| Version | Date       | Change                                            | Author               |
+=========+============+===================================================+======================+
| V 3.0   | 2025-06-03 | Initial version for damage scenario config        | Vishnu Viswanath     |
+---------+------------+---------------------------------------------------+----------------------+
|         |            |                                                   |                      |
+---------+------------+---------------------------------------------------+----------------------+
|         |            |                                                   |                      |
+---------+------------+---------------------------------------------------+----------------------+
|         |            |                                                   |                      |
+---------+------------+---------------------------------------------------+----------------------+
"""


from models.helper import DS_impact_menu, DS_impactcatagory_menu

PROPERTY_CONFIG = [
    {"label": "ID", "type": "line", "readonly": True},
    {"label": "Name", "type": "multiline", "signal": "on_DS_property_name_changed"},
     {
        "label": "Impact",
        "type": "singleselect",
        "items": ["Select"] + DS_impact_menu,    # <-- prepend 'Select'
        "signal": "on_DS_property_impact_changed"
    },
    {
        "label": "Impact Category",
        "type": "multiselect",
        "items": ["Select"] + DS_impactcatagory_menu,  # Optional: add 'Select' for consistency
        "signal": "on_DS_property_impactcategory_changed"
    },
    {"label": "Reasoning", "type": "multiline", "signal": "on_DS_property_description_changed"},
    {"label": "Comments", "type": "multiline", "signal": "on_DS_property_comment_changed"}
]

SAVE_BUTTON = {
    "enabled": True,
    "style_attr": "property_save_button_style"
}
