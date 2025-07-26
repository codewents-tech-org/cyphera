from PyQt5.QtWidgets import QMenuBar

def create_menu_bar(window, P):
    menubar = QMenuBar(window)
    menubar.setStyleSheet(f"background-color: {P.ToolBox_bg}; border: none;")
    window.setMenuBar(menubar)

    # File menu
    file_menu = menubar.addMenu("File")
    new_action = file_menu.addAction("New")
    new_action.triggered.connect(window.add_action)
    open_action = file_menu.addAction("Open")
    open_action.triggered.connect(window.open_action)
    save_action = file_menu.addAction("Save")
    save_action.triggered.connect(window.save_action)
    file_menu.addSeparator()
    exit_action = file_menu.addAction("Exit")
    exit_action.triggered.connect(window.exit_action)

    # Edit menu
    edit_menu = menubar.addMenu("Edit")
    undo_action = edit_menu.addAction("Undo")
    undo_action.triggered.connect(window.undo_action)
    redo_action = edit_menu.addAction("Redo")
    redo_action.triggered.connect(window.redo_action)

    # View menu
    view_menu = menubar.addMenu("View")
    toolbar_action = view_menu.addAction("Toggle Toolbar")
    toolbar_action.setCheckable(True)
    toolbar_action.setChecked(True)
    toolbar_action.triggered.connect(window.toggle_toolbar)

    # Help menu
    help_menu = menubar.addMenu("Help")
    help_menu.triggered.connect(window.help_action)
    help_action = help_menu.addAction("Help Contents")

