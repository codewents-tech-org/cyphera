"""
Module: AFR Level Calculator      \n 
File: afr_level_calculation.py      \n
Layer: Backend / calculation    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-07-02     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n


Description:
------------
Provides a utility function that translates a numeric AFR score into a qualitative label.
These labels are used throughout the application for visualization and reporting.

Categories:
------------
- 0 to 13   : High
- 14 to 19  : Medium
- 20 to 24  : Low
- 25+       : Very Low

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-07-02           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

def calculate_afr_Level(value):
    """
    Categorizes the numeric AFR value into a qualitative level.

    Args:
        value (int): AFR score (0 and above).

    Returns:
        str: One of "High", "Medium", "Low", "Very Low" based on thresholds.
    """
    afr_level = ''
    if value >= 0 and value <= 13:
        afr_level = "High"
    elif value >= 14 and value <= 19:
        afr_level = "Medium"
    elif value >= 20 and value <= 24:
        afr_level = "Low"
    else:
        afr_level = "Very Low"
    return afr_level