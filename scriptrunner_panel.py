#-------------------------------------------------
#-SCRIPTRUNNER_TOOL.py (Mode switch: LOCAL | FILE)
#-------------------------------------------------
from .global_settings import *
import re

# ================== PANEL =================
class XTD_PT_ScriptRunner(bpy.types.Panel):
    bl_label = "SCRIPT RUNNER"
    bl_idname = "XTD_PT_script_runner"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"

    @classmethod
    def poll(cls, context):
        return VisibilityController.check_visibility(context, panel_name="scriptrunner_panel", require_selected=True)

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        box = layout.box()
        row = box.row()
        row.label(text="Python Script Executor", icon="CONSOLE")

        row = box.row()
        row.prop(scene, "script_runner_mode", expand=True)

        if scene.script_runner_mode == "LOCAL":
            row = box.row()
            row.prop(scene, "script_runner_selected", text="")
        else:
            row = box.row()
            row.prop(scene, "script_runner_filepath", text="")

        row = box.row()
        row.operator("xtd_tools.run_script", text="Run Script", icon="PLAY")

# ================ PROPERTYS ================
bpy.types.Scene.script_runner_mode = bpy.props.EnumProperty(
    name="Mode",
    description="Choose the script execution mode",
    items=[
        ("LOCAL", "LOCAL", "Run from Blender Text Editor"),
        ("FILE", "FILE", "Run from external Python file")
    ],
    default="LOCAL"
)

def update_script_list(self, context):
    return [(text.name, text.name, "") for text in bpy.data.texts]

bpy.types.Scene.script_runner_selected = bpy.props.EnumProperty(
    name="Script",
    description="Select a script from the project",
    items=update_script_list
)

bpy.types.Scene.script_runner_filepath = bpy.props.StringProperty(
    name="Script File",
    description="Select a Python script file",
    default="",
    subtype='FILE_PATH'
)

# ================ OPERATOR ================
class XTD_OT_RunScript(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.run_script"
    bl_label = "Run Script"
    bl_description = "Execute the selected script on all selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        scene = bpy.context.scene

        if scene.script_runner_mode == "LOCAL":
            script_name = scene.script_runner_selected
            active_script = bpy.data.texts.get(script_name)
            
            if not active_script:
                self.report({'WARNING'}, "Selected script not found.")
                return {'CANCELLED'}

            script = active_script.as_string()
        
        else:
            script_path = bpy.path.abspath(scene.script_runner_filepath).strip()
            if not script_path or not os.path.exists(script_path):
                self.report({'WARNING'}, "Invalid script file path.")
                return {'CANCELLED'}

            with open(script_path, 'r') as file:
                script = file.read()

        try:
            script = re.sub(r'\bbpy\.context\.object\b', 'obj', script)

            area = next((area for area in bpy.context.screen.areas if area.type == 'VIEW_3D'), None)
            if area:
                with bpy.context.temp_override(area=area):
                    exec(script, {"obj": obj, "bpy": bpy})
            else:
                exec(script, {"obj": obj, "bpy": bpy})

        except Exception as e:
            self.report({'ERROR'}, f"Script error: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}
