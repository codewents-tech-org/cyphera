"""
Module Name   : security_goals_config.py  \n
Layer         : Configuration / Security Goals  \n
Component ID  : N/A  \n
Requirement ID: N/A  \n
Version       : V 3.0  \n
Created By    : Vishnu Viswanath  \n
Created On    : 2025-06-03  \n

Purpose:
--------
Defines the configuration schema for Security Goal property input fields used in dynamic
property panels. Enables standardized rendering and interaction logic for security goal entities.

Description:
------------
Outlines the field configurations for Security Goals in the property UI, covering input types,
signal handlers, data sources, and editable states. The configuration is used to generate UI
components and handle updates uniformly.

Responsibilities:
-----------------
- Describe UI field metadata for Security Goal editing/viewing
- Emit property change signals for integration with logic layers
- Link external data (e.g., responsible party menus)

Structure:
----------
+---------------------+----------------+----------------------------------------------------+--------------------------------------+
| Property Label      | Input Type     | Signal                                             | Additional Params                    |
+=====================+================+====================================================+======================================+
| ID                  | line           | None                                               | readonly=True                        |
| Name                | multiline      | on_sg_property_name_changed                        | -                                    |
| Responsible         | multiselect    | on_sg_property_securityproperty_changed            | items=RA_Responsible_menu            |
| TOE Configuration   | multiselect    | on_sg_property_toe_configuration_property_changed  | -                                    |
| Description         | multiline      | on_sg_property_description_changed                 | -                                    |
| Comments            | multiline      | on_sg_property_comment_changed                     | -                                    |
+---------------------+----------------+----------------------------------------------------+--------------------------------------+

Dependencies:
-------------
- models.helper.RA_Responsible_menu
- property_input_components.PropertyInputFactory (consumes this config)

Limitations:
------------
- Static field set; no conditional visibility or validation
- Responsible item list must be preloaded

Improvements:
-------------
- Add validation and conditional rendering support
- Enable support for dynamic value sources per field

Change History:
---------------
+---------+------------+-------------------------------------------------------------+----------------------+
| Version | Date       | Change                                                      | Author               |
+=========+============+=============================================================+======================+
| V 3.0   | 2025-06-03 | Initial version for security goals property config          | Vishnu Viswanath     |
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
        "signal": "on_sg_property_name_changed"
    },
    {
        "label": "Responsible",
        "type": "multiselect",
        "signal": "on_sg_property_responsible_changed"
    },
    {
        "label": "TOE Configuration",
        "type": "multiselect",
        "signal": "on_sg_property_toe_configuration_changed"
    },
    {
        "label": "Description",
        "type": "multiline",
        "signal": "on_sg_property_description_changed"
    },
    {
        "label": "Comments",
        "type": "multiline",
        "signal": "on_sg_property_comments_changed"
    }
]


SAVE_BUTTON = {
    "enabled": True
}
