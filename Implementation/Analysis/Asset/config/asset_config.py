"""
Module Name   : asset_config.py \n
Layer         : Configuration / Asset \n
Component ID  : N/A  \n
Requirement ID: N/A  \n
Version       : V 3.0  \n
Created By    : Vishnu Viswanath  \n
Created On    : 2025-06-03  \n

Purpose:
--------
Defines the configuration schema for Asset property input fields used in dynamic
property panels. This allows the UI layer to render consistent input widgets
based on configuration rather than hardcoded logic.

Description:
------------
Specifies the input fields shown for an Asset in the property panel,
including type, labels, readonly status, selectable items, and signal handlers.
Also defines the configuration for the Save button appearance and state.

Responsibilities:
-----------------
- Provide a declarative config for UI input generation
- Define signal mappings for property changes
- Standardize save button styling across the Asset module

Structure:
----------
+------------------------+----------------+---------------------------------------------+------------------------------------+
| Property Label         | Input Type     | Signal                                      | Additional Params                  |
+========================+================+=============================================+====================================+
| ID                     | line           | None                                        | readonly=True                      |
| Name                   | multiline      | on_asset_property_name_changed              | -                                  |
| Security Properties    | multiselect    | on_asset_property_securityproperty_changed  | items=assert_securityproperty_menu |
| Description            | multiline      | on_asset_property_description_changed       | -                                  |
| Comments               | multiline      | on_asset_property_comment_changed           | -                                  |
+------------------------+----------------+---------------------------------------------+------------------------------------+

Dependencies:
-------------
- models.helper.assert_securityproperty_menu
- property_input_components.PropertyInputFactory (consumes this config)

Limitations:
------------
- Field validation logic must be handled externally
- Input types are fixed to known types by the UI factory

Improvements:
-------------
- Add field-level validation hooks
- Support optional field groups or tabs for better UI organization

Change History:
---------------
+----------------+----------------------+---------------------------------------------+----------------------+
| Version        | Date                 | Change                                      | Author               |
+================+======================+=============================================+======================+
| V 3.0          | 2025-06-03           | Initial version for asset property config   | Vishnu Viswanath     |
+----------------+----------------------+---------------------------------------------+----------------------+
|                |                      |                                             |                      |
+----------------+----------------------+---------------------------------------------+----------------------+
|                |                      |                                             |                      |
+----------------+----------------------+---------------------------------------------+----------------------+
|                |                      |                                             |                      |
+----------------+----------------------+---------------------------------------------+----------------------+
"""


from models.helper import assert_securityproperty_menu

PROPERTY_CONFIG = [
    {"label": "ID", "type": "line", "readonly": True},
    {"label": "Name", "type": "multiline", "signal": "on_asset_property_name_changed"},
    {"label": "Security Properties", "type": "multiselect", "items": assert_securityproperty_menu, "signal": "on_asset_property_securityproperty_changed"},
    {"label": "Description", "type": "multiline", "signal": "on_asset_property_description_changed"},
    {"label": "Comments", "type": "multiline", "signal": "on_asset_property_comment_changed"}
]

SAVE_BUTTON = {
    "enabled": True,
    "style_attr": "property_save_button_style"
}
