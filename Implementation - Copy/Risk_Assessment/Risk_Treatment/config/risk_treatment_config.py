"""
Module Name   : risk_treatment_config.py  \n
Layer         : Configuration / Risk Treatment  \n
Component ID  : N/A  \n
Requirement ID: N/A  \n
Version       : V 3.0  \n
Created By    : Vishnu Viswanath  \n
Created On    : 2025-06-03  \n

Purpose:
--------
Defines the configuration schema for Risk Treatment property input fields used in dynamic
property panels. Enables UI components to be rendered and wired consistently via configuration.

Description:
------------
Specifies the input fields shown in the Risk Treatment property panel, including input type,
label, read-only status, item lists, and signal handlers. Also defines Save button appearance
and functionality.

Responsibilities:
-----------------
- Provide structured metadata for UI component generation
- Define update signals for interactive fields
- Link external data sources like treatment options and multiselect items

Structure:
----------
+-----------------------+----------------+---------------------------------------------------+--------------------------------------+
| Property Label        | Input Type     | Signal                                            | Additional Params                    |
+=======================+================+===================================================+======================================+
| ID                    | line           | None                                              | readonly=True                        |
| Damage                | multiline      | None                                              | readonly=True                        |
| Impact                | line           | None                                              | readonly=True                        |
| Threat                | multiline      | None                                              | readonly=True                        |
| Initial AFR           | line           | None                                              | readonly=True                        |
| Initial Risk          | line           | None                                              | readonly=True                        |
| Resid AFR             | line           | None                                              | readonly=True                        |
| Resid Risk            | line           | None                                              | readonly=True                        |
| TOE Configuration     | multiselect1   | on_rt_property_toe_configuration_property_changed | -                                    |
| Risk Treatment        | multiselect    | on_rt_property_rt_changed                         | items=risktreatement                 |
| Security Claims       | multiselect    | on_rt_property_sc_changed                         | -                                    |
| Security Goals        | multiselect    | on_rt_property_sg_changed                         | -                                    |
| Mitigated By          | line           | None                                              | readonly=True                        |
+-----------------------+----------------+---------------------------------------------------+--------------------------------------+

Dependencies:
-------------
- models.helper.risktreatement
- property_input_components.PropertyInputFactory (consumes this config)

Limitations:
------------
- Field values and validation are not dynamically derived
- multiselect1 item source is not defined here

Improvements:
-------------
- Add dynamic field value population
- Introduce validation and dependency mapping between fields

Change History:
---------------
+---------+------------+------------------------------------------------------------+----------------------+
| Version | Date       | Change                                                     | Author               |
+=========+============+============================================================+======================+
| V 3.0   | 2025-06-03 | Initial version for risk treatment property config         | Vishnu Viswanath     |
+---------+------------+------------------------------------------------------------+----------------------+
|         |            |                                                            |                      |
+---------+------------+------------------------------------------------------------+----------------------+
|         |            |                                                            |                      |
+---------+------------+------------------------------------------------------------+----------------------+
|         |            |                                                            |                      |
+---------+------------+------------------------------------------------------------+----------------------+
"""


from models.helper import risktreatement

PROPERTY_CONFIG = [
    {
        "label": "ID",
        "type": "line",
        "readonly": True
    },
    {
        "label": "Damage",
        "type": "multiline",
        "readonly": True
    },
    {
        "label": "Impact",
        "type": "line",
        "readonly": True
    },
    {
        "label": "Threat",
        "type": "multiline",
        "readonly": True
    },
    {
        "label": "Initial AFR",
        "type": "line",
        "readonly": True
    },
    {
        "label": "Initial Risk",
        "type": "line",
        "readonly": True
    },
    {
        "label": "Resid AFR",
        "type": "line",
        "readonly": True
    },
    {
        "label": "Resid Risk",
        "type": "line",
        "readonly": True
    },
    {
        "label": "TOE Configuration",
        "type": "multiselect1",
        "signal": "on_rt_property_toe_configuration_property_changed"
    },
    {
        "label": "Risk Treatment",
        "type": "multiselect",
        "items": risktreatement,
        "signal": "on_rt_property_rt_changed"
    },
    {
        "label": "Security Claims",
        "type": "multiselect",
        "signal": "on_rt_property_sc_changed"
    },
    {
        "label": "Security Goals",
        "type": "multiselect",
        "signal": "on_rt_property_sg_changed"
    },
    {
        "label": "Mitigated By",
        "type": "line",
        "readonly": True
    }
]

SAVE_BUTTON = {
    "enabled": True,
    "text": "Save"
}
