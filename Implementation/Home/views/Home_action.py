"""
Module Name   : Home_action.py
Layer         : Presentation / UI Panel
Component ID  : CY_UI_001
Requirement ID: N/A
Version       : V 3.0
Created By    : Vishnu Viswanath
Created On    : 2025-05-14

Purpose:
--------
Defines the main UI components for project home screen actions including creation, opening,
and recent project management in the TARA (Threat Analysis and Risk Assessment) Tool.

Description:
------------
Implements PyQt5-based interactive panels:
- Home panel with "New Project", "Open Project", and "Recents"
- New Project panel with project metadata inputs
- Open Project panel with project file selection
- Import Project stub panel for future integration

Responsible for initializing the project structure, saving metadata (author, client, supplier),
and updating internal paths and configuration files (.tara and SQLite DB).

Responsibilities:
-----------------
- Handle user interactions for project lifecycle management
- Create and initialize project folder, files, and configuration
- Save metadata into SQLite (`project_info` table)
- Maintain list of recent projects
- Route project loading to relevant modules

Panels:
-------
+----------------------+----------------------------+
| Panel Class          | Purpose                    |
+======================+============================+
| MainHome_Panel       | Project launch and summary |
+----------------------+----------------------------+
| MainNew_Panel        | New project creation form  |
+----------------------+----------------------------+
| MainOpen_Panel       | Open existing project      |
+----------------------+----------------------------+
| MainImport_Panel     | Placeholder for import     |
+----------------------+----------------------------+

Dependencies:
-------------
- PyQt5
- qtawesome
- styles (UI stylesheets)
- utils (file handling, interface routing)
- controllers.DatabaseCreator
- models.Parameters
- models.helper

Limitations:
------------
- Only one methodology ("Attack Potential") currently supported
- Import panel is not implemented
- No built-in validation for client/supplier fields

Improvements:
-------------
- Add multiple methodology support in dropdown
- Persist additional project metadata (versioning, timestamp)
- Enable multi-user collaboration metadata
- Implement Import Panel with XML/JSON migration support

Change History:
---------------
+---------+------------+----------------------------------------------+----------------------+
| Version | Date       | Change                                       | Author               |
+=========+============+==============================================+======================+
| V 3.0   | 2025-06-04 | Added organization + client/supplier storage | Vishnu Viswanath     |
+---------+------------+----------------------------------------------+----------------------+
|         |            |                                              |                      |
+---------+------------+----------------------------------------------+----------------------+
"""


# views/Home_action.py

# Home/views/Home_action.py

from .MainHomePanel import MainHome_Panel
from .MainNewPanel import MainNew_Panel
from .MainOpenPanel import MainOpen_Panel
from .MainImportPanel import MainImport_Panel
from .NameLabel import NameLabel
from .PathLabel import PathLabel

__all__ = [
    "MainHome_Panel",
    "MainNew_Panel",
    "MainOpen_Panel",
    "MainImport_Panel",
    "NameLabel",
    "PathLabel"
]
