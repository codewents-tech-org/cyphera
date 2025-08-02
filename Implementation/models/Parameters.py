
Project_name = ''
Author_name = ''
Client_name = ''
Supplier_name = ''
selected_methedology = ''

default_organization = "DefaultORG"
SQLALCHEMY_DATABASE_URL=""
project_path = ''
database_file_path = 'database.db'
recent_database_file_path = 'recent_database_path.db'
Footer_databse_file_path = 'Footer_Database.db'
GenerateReport_path = ''
GeneratePdfReport_path = ''
GeneratePENTestReport_path = ''
GeneratePENTestPdfReport_path = ''
selected_cloud_folder = ""      # 📁 Current selected folder on cloud UI
selected_cloud_file = ""        # 📄 Current selected .tara file
remote_project_path = ""        # 🌐 Full path to selected .tara (REMOTE_BASE_PATH + /folder/file)


ssh_transport = None           # Store active SSH session
sftp = None                    # Store active SFTP session
project_storage_mode = 'local'  # or 'cloud'

db_type = ''                  # 'postgres', 'sqlite', etc.
db_user = ''
db_password = ''
db_host = ''
db_port = ''
current_db_name = ''
#===== Colour Parameters =====#

Black = '#151515'
LightGray = "#E2DAD6"
shadeGray = "#F0F0F0"
Red = "#FF0000"
Yellow = "#F9E400"
Green = "#00FF00"
White = '#FFFFFF'
Gray = "#AAAAAA"
TC1 = '#33313B'
TC2 = '#4592AF' 

Box_blue = '#0cc0df' 

# Module_bg = '#46afc8'
# SubModule_gradiant1_bg = '#68bdd1'
# SubModule_gradiant2_bg = '#33d687'
# line_gradiant1_bg = '#0097b2'
# line_gradiant2_bg = '#7ed597'
# line_gradiant3_bg = '#ff5757'


#===== Panel Colour Parameters =====#
ToolBox_bg = '#EEEEEE'
ToolBoxGroup_bg = LightGray
Logo_bg = Gray
Module_bg = '#FFFFFF'
Action_bg = '#F6F7FB'
Action_border_color = '#E3E5EC'
footer_bg = '#009D9C'
SubModuleSidebar_bg = '#F6F7FB'
ModuleHighlight_bg = '#AFC8AD'
ModuleHighlightColor = '#009D9C'

SubModuleAText_fg = '#1e331e'
SubModuleIAText_fg = '#3d663d'

HighlightColor = '#009D9C'

Tab_bg = White
rowhighlight_bg = '#F2F2F2'

AFRLevel_High_bg = '#0097b2'
AFRLevel_Medium_bg = '#0cc0df'
AFRLevel_Low_bg = '#5ce1e6'
AFRLevel_VeryLow_bg = '#cefdff'

AttackPath_highlight = '#E5B511'

#===== ToolBar Icons =====#

Report_Logo = 'assets/Images/EK_Logo.png'
Report_footer_Logo = 'assets/Images/EK_Footer_Logo.png'
Footer_placeholder = 'assets/Images/placeholder footer.png'


#===== Home Icons =====#
newproject_icon = "assets/Images/new_project.png"
openproject_icon = "assets/Images/open_project.png"
importproject_icon = "assets/Images/import_project.png"

#===== ToolBar Icons =====#
Home_icon = "assets/Images/Home.svg"
home_icon = "assets/Images/home.png"
open_icon = "assets/Images/open.png"
save_icon = "assets/Images/save.png"
undo_icon = "assets/Images/undo.png"
redo_icon = "assets/Images/redo.png"
setting_icon = "assets/Images/setting.png"
help_icon = "assets/Images/help.png"
forward_icon = "assets/Images/forward.png"
backward_icon = "assets/Images/backward.png"
italic_icon = "assets/Images/italic.svg"
add_icon = "assets/Images/add.png"
bold_icon = "assets/Images/bold.svg"
delete_icon = "assets/Images/delete.png"
import_icon = "assets/Images/import.png"
new_icon = "assets/Images/new.png"
rightarrow_icon = "assets/Images/right_arrow.png"
downarrow_icon = "assets/Images/down_arrow.png"
local_icon = "assets/Images/local_icon.svg"
cloud_icon = "assets/Images/cloud_icon.svg"
#===== Module Icons =====#
TargetOfEvaluation_icon = "assets/Images/target_of_Evaluation.svg"
Analysis_icon = "assets/Images/analysis.svg"
SecurityControl_icon = "assets/Images/security_measurement.svg"
catalog_icon = "assets/Images/catalog.svg"
AttackPaths_icon = "assets/Images/attack_paths.svg"
RiskAssessment_icon = "assets/Images/risk_assessment.svg"
Summary_icon = "assets/Images/summary.svg"
AnalysisTable_icon = "assets/Images/Analysis_tables.png"
TOETable_icon = "assets/Images/TOE_tables.png"
downarrow_icon = "assets/Images/downarrow.png"
profile_icon = "assets/Images/profile.svg"
id_icon = "assets/Images/ID.png"
name_icon = "assets/Images/name.png"
securityproperty_icon = "assets/Images/property.png"
description_icon = "assets/Images/content.png"
comment_icon = "assets/Images/comment.png"
selectedrow_icon    = "assets/Images/selectedraw.svg"
deselectedrow_icon = "assets/Images/default_selected_row.png"
edit_icon = "assets/Images/Edit_fill.svg"
subtask_icon = "assets/Images/selected_tree.svg"
threat_icon = "assets/Images/threat.png"
impact_icon = "assets/Images/impact.png"
impactcategory_icon = "assets/Images/impact_category.png"
profile_icon = "assets/Images/profile.svg"
assets_icon = "assets/Images/assets.png"
damagescenario_icon = "assets/Images/damagescenario.png"
InitAFR_icon = "assets/Images/init_afr.png"
ResidAFR_icon = "assets/Images/resid_afr.png"
Report_icon = "assets/Images/report.svg"
assum_icon = "assets/Images/assum.png"
attacktree_icon = "assets/Images/attacktree_table.png"
RiskControlTree_icon = "assets/Images/attacktree_table.png"
securityclaims_icon = "assets/Images/RiskAssessment_table.png"
securitygoals_icon = "assets/Images/RiskAssessment_table.png"
risktreatement_icon = "assets/Images/RiskAssessment_table.png"
time_icon = "assets/Images/time.png"
Expertise_icon = "assets/Images/Expertise.png"
Knowledge_icon = "assets/Images/Knowledge.png"
Access_icon = "assets/Images/Access.png"
Equipment_icon = "assets/Images/Equipment.png"
responsible_icon = "assets/Images/responsible.png"
sclaims_icon = "assets/Images/security_claims.png"
sgoals_icon = "assets/Images/security_goals.png"
mitigate_icon = "assets/Images/mitigates.png"
decision_icon = "assets/Images/risk_decision.png"
# Threat_Catalog_icon = "assets/Images/Threat_Catalog.png"

#===== AttackTree Icons =====#
headnode_icon = "assets/Attack_Assets/headNode.png"
# Analysis_icon = "images/normal/Analysis.png"
# AttackPaths_icon = "images/normal/AttackPaths.png"
# RiskAssessment_icon = "images/normal/RiskAssessment.png"
# Summary_icon = "images/normal/Summary.png"
# exit_icon = "images/pro/exit.png"
loader_icon = "assets/Images/loader.svg"
loader_gif = "assets/Images/loader.gif"
#===== Asset Icons =====#
Reload_icon = "assets/Images/refresh.png"
addrow_icon = "assets/Images/addrow.png"
deleterow_icon = "assets/Images/deleterow.png"
updatedatabase_icon = "assets/Images/updatedatabase.png"
updatedone_icon = "assets/Images/updatedone.png"
close_icon = "assets/Images/close.png"
show_property_icon = "assets/Images/show_property.png"


#===== TOE Description Icons =====#
highlight_icon = "assets/Images/highlight.svg"
text_color_icon = "assets/Images/text_color.png"
left_align_icon = "assets/Images/left_align.png"
justify_icon = "assets/Images/align_justify.svg"
center_align_icon = "assets/Images/center_align.png"
right_align_icon = "assets/Images/right_align.png"
number_index_icon = "assets/Images/number_index.png"
bullet_index_icon = "assets/Images/bullet_index.png"
insert_image_icon = "assets/Images/insert_image.png"
insert_table_icon = "assets/Images/insert_table.png"
insert_row_above_icon = "assets/Images/insert_row_above.png"
insert_row_below_icon = "assets/Images/insert_row_below.png"
delete_row_icon = "assets/Images/delete_row.png"
insert_column_left_icon = "assets/Images/insert_column_left.png"
insert_column_right_icon = "assets/Images/insert_column_right.png"
delete_column_icon = "assets/Images/delete_column.png"


#===== Generate Report Icons =====#
generatereport_icon = "assets/Images/generate.png"
openreport_icon = "assets/Images/openreport.png"
downloadreport_icon = "assets/Images/download.png"

#===== Attack Paths assets =====#
assets = {
    "head_node" : "assets/Attack_Assets/head_node.png",
    "intermediate_node" : "assets/Attack_Assets/intermediate_node.png",
    "leaf_node" : "assets/Attack_Assets/leaf_node.png",
    "and_gate" : "assets/Attack_Assets/and_gate.png",
    "or_gate" : "assets/Attack_Assets/or_gate.png",
    "head_node_high_high" : "assets/Attack_Assets/head_node_high_high.png",
    "head_node_high_medium" : "assets/Attack_Assets/head_node_high_medium.png",
    "head_node_high_low" : "assets/Attack_Assets/head_node_high_low.png",
    "head_node_high_verylow" : "assets/Attack_Assets/head_node_high_verylow.png",
    "head_node_medium_high" : "assets/Attack_Assets/head_node_medium_high.png",
    "head_node_medium_medium" : "assets/Attack_Assets/head_node_medium_medium.png",
    "head_node_medium_low" : "assets/Attack_Assets/head_node_medium_low.png",
    "head_node_medium_verylow" : "assets/Attack_Assets/head_node_medium_verylow.png",
    "head_node_low_high" : "assets/Attack_Assets/head_node_low_high.png",
    "head_node_low_medium" : "assets/Attack_Assets/head_node_low_medium.png",
    "head_node_low_low" : "assets/Attack_Assets/head_node_low_low.png",
    "head_node_low_verylow" : "assets/Attack_Assets/head_node_low_verylow.png",
    "head_node_verylow_high" : "assets/Attack_Assets/head_node_verylow_high.png",
    "head_node_verylow_medium" : "assets/Attack_Assets/head_node_verylow_medium.png",
    "head_node_verylow_low" : "assets/Attack_Assets/head_node_verylow_low.png",
    "head_node_verylow_verylow" : "assets/Attack_Assets/head_node_verylow_verylow.png",
    "leaf_node_included" : "assets/Attack_Assets/leaf_node_included.png"
}




