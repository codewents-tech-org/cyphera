from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt5.QtCore import pyqtSignal

import Risk_Assessment.controllers.riskassessment_TableValueLoad as TVL
import Risk_Assessment.controllers.riskassessment_TableSaveRecord as TSR
import Risk_Assessment.controllers.riskassessment_PropertyValueDisplay as PVD
from Risk_Assessment.Risk_Treatment.views.risktreatment_toolbar_panel import create_toolbar
from Risk_Assessment.Risk_Treatment.config.risk_treatment_config import PROPERTY_CONFIG, SAVE_BUTTON
from controllers.schema_manager import get_instances
from controllers.tablemodel import SecurityGoals, SecurityClaims, TOEConfiguration
from components.propertypanel.property_input_components import PropertyInputFactory
from styles.property_panel_style import property_save_button_style
import controllers.TableValueHighlight as TVH
import components.action_panel as action_panel
import components.table.table_panel as table_panel
import components.propertypanel.property_panel_layout as property_panel_layout
from components.loading_dialog import RoundLoader
import Analysis.models.analysis_synchronization as AS
import utils.interface_utils as interfaces
import components.table.table_row_indicator as TRI


class RiskTreatement_Module(QWidget):
    create_property_panel_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.row_selected.connect(self.display_row_data_in_panel)

        # Internal Maps and Control Lists
        self.HEIGHT_MAP = {}
        self.STYLE_MAP = {}
        self.threat_property_controls = []

        # ✅ Setup Property Panel
        self.property_panel_manager = property_panel_layout.PropertyPanelManager(self)
        self.property_panel_manager.create_property_panel()

        self.toggle_button = self.property_panel_manager.toggle_button
        self.property_panel = self.property_panel_manager.property_panel
        self.property_layout = self.property_panel_manager.property_layout

        self.create_property_panel_signal.connect(self.build_property_panel)
        self.create_property_panel_signal.emit()

        # ✅ Main Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # ✅ Toolbar and Action Panel
        create_toolbar(self)
        main_layout.addWidget(self.toolbar)

        action_panel.create_action_panel(self)

        # ✅ Table Setup
        self.table_wrapper = table_panel.TablePanelWrapper(
            use_row_indicator=True, use_tree_indicator=False, parent=self
        )
        self.table_wrapper.create_table_panel()
        self.table_wrapper.set_headers("risktreatment")  # ✅ Correct header for Risk Treatment

        self.table = self.table_wrapper.table
        self.table_layout = self.table_wrapper.table_layout

        # ✅ Add table + property panel to layout
        self.action_panel_layout.addWidget(self.table_wrapper.table)
        self.action_panel_layout.addWidget(self.property_panel_manager.switch_property_panel)
        self.action_panel_layout.addWidget(self.property_panel_manager.property_panel)
        main_layout.addWidget(self.action_panel)

        # ✅ Buttons (only submit + save if needed)
        self.submit_button.setEnabled(False)
        self.save_button.setEnabled(False)

        self.submit_button.clicked.connect(self.submit_changes)
        self.save_button.clicked.connect(self.submit_changes)

        # ✅ Table signal connections
        self.table.itemChanged.connect(self.update_button_states)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)

        self.update_button_states()
        self.previous_text = None

    def load_data(self):
        self.loader = RoundLoader(self, label_text="Loading Risk Treatment Data...")
        self.loader.show()
        QApplication.processEvents()

        try:
            AS.update_risktreatement_data()

            goals = get_instances(SecurityGoals, {'is_deleted': False})
            claims = get_instances(SecurityClaims, {'is_deleted': False})
            toes = get_instances(TOEConfiguration, {'is_deleted': False})

            self.SG_list = [f"{g.sg_id}::{g.name}" for g in goals if g.sg_id and g.name]
            self.SC_list = [f"{c.sc_id}::{c.name}" for c in claims if c.sc_id and c.name]
            self.formatted_toe_configuration = [
                f"{t.toe_configuration_id}::{t.toe_configuration_name}"
                for t in toes if t.toe_configuration_id and t.toe_configuration_name
            ]

            self.rt_security_goals_input.additem(self.SG_list)
            self.rt_security_claims_input.additem(self.SC_list)
            self.rt_toe_configuration_input.additem(self.formatted_toe_configuration)

            TVL.load_risktreatement(self, self.table, self.property_panel_manager.property_panel, self.property_panel_manager.toggle_button)
            interfaces.unsaved_changes = False

        finally:
            self.loader.close()

    def submit_changes(self):
        self.table.setFocus()
        TSR.risktreatment_submit_changes(self.table)
        AS.remove_claims_from_risk_data()
        AS.remove_toe_configurations_from_risk_data()
        self.update_button_states()
        interfaces.unsaved_changes = False

    def build_property_panel(self):
        self.property_factory = PropertyInputFactory()
        self.rt_property_controls = []

        for field in PROPERTY_CONFIG:
            widget = self.property_factory.create_common_property_input(
                field["label"], field["type"], self.property_layout,
                self.rt_property_controls,
                getattr(self, field.get("signal")) if field.get("signal") else None,
                field.get("items")
            )
            if field.get("readonly"):
                widget.setReadOnly(True)
            setattr(self, f'rt_{field["label"].lower().replace(" ", "_")}_input', widget)

        if SAVE_BUTTON.get("enabled"):
            self.save_button = self.property_factory.create_save_button(
                layout=self.property_layout,
                style=property_save_button_style,
                controls_list=self.rt_property_controls,
                signal=self.property_save_clicked,
                sender="Property panel"
            )
            self.save_button.setEnabled(False)

        self.property_save_clicked.connect(self.handle_property_save_signal)

    def handle_property_save_signal(self, payload):
        print(f"[SAVE] Payload from property panel: {payload}")

    def update_button_states(self):
        has_data = self.table.rowCount() > 0
        if hasattr(self, 'save_button'):
            self.save_button.setEnabled(has_data)
        self.submit_button.setEnabled(has_data)

    def on_row_selection_changed(self, selected, deselected):
        current_row = self.table.currentRow()
        print(f"[DEBUG] Current selected row: {current_row}")

        # ✅ Update property panel
        if current_row >= 0:
            self.display_row_data_in_panel(None)

            # ✅ Emit row data
            data = {}
            headers = [
                "ID", "Damage", "Impact", "Threat", "Initial AFR", "Initial Risk",
                "Resid AFR", "Resid Risk", "TOE Configuration", "Risk Treatment",
                "Security Claims", "Security Goals", "Mitigated By"
            ]
            for col, header in enumerate(headers, start=1):  # Assumes column 0 is SidebarWidget
                item = self.table.item(current_row, col)
                data[header] = item.text() if item else ""
            payload = {"sender": "Table", "event": "row_selected", "data": data}
            self.row_selected.emit(payload)

        # ✅ Update dot highlight
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if isinstance(widget, TRI.SidebarWidget):
                is_selected = (row == current_row)
                print(f"[DEBUG] → Row {row}: SidebarWidget.set_selected({is_selected})")
                widget.set_selected(is_selected)
                # widget.set_selected(row == current_row)

        # ✅ Track selection for unsaved detection
        # TVH.on_row_selection_changed(self.table)

        # ✅ Update Save/Add/Delete/etc. buttons
        self.update_button_states()

    def display_row_data_in_panel(self, data):
        PVD.RiskTreatment_display_selected_row(
            self.table,
            self.rt_property_controls,
            self.SC_list,
            self.SG_list,
            self.property_panel_manager.property_panel,
            self.property_panel_manager.toggle_button
        )

    def on_rt_property_toe_configuration_property_changed(self):
        PVD.on_property_multiselect_changed(self.table, 9, self.rt_toe_configuration_input)

    def on_rt_property_rt_changed(self):
        PVD.on_property_multiselect_changed(self.table, 10, self.rt_risk_treatment_input)

    def on_rt_property_sc_changed(self):
        PVD.on_property_multiselect_changed(self.table, 11, self.rt_security_claims_input)

    def on_rt_property_sg_changed(self):
        PVD.on_property_multiselect_changed(self.table, 12, self.rt_security_goals_input)
    
    def set_unsaved_changes(self, status: bool):
        """
        Placeholder method to track unsaved changes in the module.
        This can be connected to save/discard logic later.
        """
        self._unsaved_changes = status


    def closeEvent(self, event):
        event.accept()
