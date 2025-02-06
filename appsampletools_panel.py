#-------------------------------------------------
#-APPSAMPLETOOLSPANEL.py | PANEL MODULE TEMPLATE FILE
#-------------------------------------------------
from .global_settings import *

# ================== PANEL =================
class XTD_PT_AppnameTools(bpy.types.Panel):
    bl_label = "APP NAME TOOLS"
    bl_idname = "XTD_PT_appnametools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"

    @classmethod
    def poll(cls, context):
        return VisibilityController.check_visibility(context, panel_name = "appsampletools_panel", require_selected=True, require_prefix=True)
        
    def draw(self, context):
        layout = self.layout
        layout.label(text="APP:")
        box = layout.box()
        for i in range(0,2,2):
            row = box.row(align=True)
            row.operator("xtd_tools.appoperator", text="RUN", icon="OBJECT_DATAMODE")
        
        layout = self.layout
        row = layout.row()
        row.alignment = 'LEFT'
        row.prop(bpy.context.scene, "xtd_tools_sampleadstoggle", text="APPS", emboss=False, icon_only=True, icon="TRIA_DOWN" if bpy.context.scene.xtd_tools_sampleadstoggle else "TRIA_RIGHT")
        if bpy.context.scene.xtd_tools_sampleadstoggle:
            box = layout.box()
            split = box.grid_flow(columns=1, align=True)
            grid.operator("xtd_tools.appoperator", text="APP", icon='MOD_REMESH')
            grid.operator("xtd_tools.appoperator", text="APP", icon='MOD_WARP')
                
# ================ SCENES ================
bpy.types.Scene.xtd_tools_sampleadstoggle = bpy.props.BoolProperty(name="APPS", default=False)
bpy.types.Scene.xtd_tools_forminput = bpy.props.StringProperty(name="", description="", default="Form Text")
bpy.types.Scene.xtd_tools_checkbox = bpy.props.BoolProperty(name="Checkbox text", description="", default=False)
bpy.types.Scene.xtd_tools_switcher = bpy.props.EnumProperty(name='Switcher label',
        items =  (
            ('YES','YES',''),
            ('NO','NO','')
        ),
        default = 'NO'
    )

# ================ OPERATORS ================
# ----------- APP OPERATOR NAME -----------
class XTD_OT_AppOperator(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.appoperator"
    bl_label = "Operator label"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        return {'FINISHED'}


