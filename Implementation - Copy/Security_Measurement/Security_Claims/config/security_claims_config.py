"""
Module Name   : security_claims_config.py  \n
Layer         : Configuration / Security Claims  \n
Component ID  : N/A  \n
Requirement ID: N/A  \n
Version       : V 3.0  \n
Created By    : Vishnu Viswanath  \n
Created On    : 2025-06-03  \n

Purpose:
--------
Defines the configuration schema for Security Claim property input fields used in dynamic
property panels. Allows consistent generation of form inputs and signals for security claim objects.

Description:
------------
Configures the fields to be shown in the Security Claim UI, including editable and readonly fields,
input types, data sources, and signal connections. Also includes settings for Save button rendering.

Responsibilities:
-----------------
- Provide field definitions for the Security Claims panel
- Wire up signal events for editable properties
- Reference external data lists like responsible parties

Structure:
----------
+---------------------+----------------+---------------------------------------------------+--------------------------------------+
| Property Label      | Input Type     | Signal                                            | Additional Params                    |
+=====================+================+===================================================+======================================+
| ID                  | line           | None                                              | readonly=True                        |
| Name                | multiline      | on_sc_property_name_changed                       | -                                    |
| Assumptions         | multiselect    | on_sc_property_assumptionproperty_changed         | -                                    |
| Responsible         | multiselect    | on_sc_property_securityproperty_changed           | items=RA_Responsible_menu            |
| TOE Configuration   | multiselect    | on_sc_property_toe_configuration_property_changed | -                                    |
| Description         | multiline      | on_sc_property_description_changed                | -                                    |
| Comments            | multiline      | on_sc_property_comment_changed                    | -                                    |
+---------------------+----------------+---------------------------------------------------+--------------------------------------+

Dependencies:
-------------
- models.helper.RA_Responsible_menu
- property_input_components.PropertyInputFactory (consumes this config)

Limitations:
------------
- Signal logic assumes handlers are predefined in parent component
- No validation or conditional field logic is embedded

Improvements:
-------------
- Add field-level validation and help text support
- Enable conditional visibility and default value binding

Change History:
---------------
+---------+------------+-------------------------------------------------------------+----------------------+
| Version | Date       | Change                                                      | Author               |
+=========+============+=============================================================+======================+
| V 3.0   | 2025-06-03 | Initial version for security claims property config         | Vishnu Viswanath     |
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
        "signal": "on_sc_property_name_changed"
    },
    {
        "label": "Assumptions",
        "type": "multiselect",
        "signal": "on_sc_property_assumptionproperty_changed"
    },
    {
        "label": "Responsible",
        "type": "multiselect",
        "signal": "on_sc_property_securityproperty_changed"
    },
    {
        "label": "TOE Configuration",
        "type": "multiselect",
        "signal": "on_sc_property_toe_configuration_property_changed"
    },
    {
        "label": "Description",
        "type": "multiline",
        "signal": "on_sc_property_description_changed"
    },
    {
        "label": "Comments",
        "type": "multiline",
        "signal": "on_sc_property_comment_changed"
    }
]

SAVE_BUTTON = {
    "enabled": True
}
